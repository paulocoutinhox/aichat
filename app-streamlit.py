import base64
import os
import uuid

import azure.cognitiveservices.speech as speechsdk
import openai
import streamlit as st
from streamlit_message import message as st_message

# application
st.title("Chatbot")

# history
if "history" not in st.session_state:
    st.session_state.history = []

# generate data
def generate_answer():
    user_message = st.session_state.input_text

    if not user_message:
        return

    # prepare chat history
    message_history = ""

    if st.session_state.history:
        for chat in st.session_state.history:
            is_picture = chat["is_picture"] if "is_picture" in chat else False
            is_audio = chat["is_audio"] if "is_audio" in chat else False
            is_user = chat["is_user"] if "is_user" in chat else False

            if not is_picture and not is_audio:
                if is_user:
                    message_history += "Q: " + chat["message"].strip() + "\n\n"
                else:
                    message_history += "A: " + chat["message"].strip() + "\n\n"

    message_history = message_history + "\n\n" + user_message
    message_history = message_history.strip()

    # call openai api
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=message_history,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0,
    )

    result_text = response.choices[0].text

    if result_text:
        result_text = result_text.strip()

    # requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get("SPEECH_KEY"),
        region=os.environ.get("SPEECH_REGION"),
    )

    os.makedirs("public/audios/", exist_ok=True)

    audio_filename = "public/audios/" + str(uuid.uuid4()) + ".mp3"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_filename)

    # the language of the voice that speaks (https://speech.microsoft.com/portal/voicegallery)
    speech_config.speech_synthesis_voice_name = "pt-BR-AntonioNeural"

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    # get text from gradio
    speech_synthesis_result = speech_synthesizer.speak_text_async(result_text).get()

    if (
        speech_synthesis_result.reason
        == speechsdk.ResultReason.SynthesizingAudioCompleted
    ):
        # print("Speech synthesized for text [{}]".format(result_text))
        pass
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))

        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

    st.session_state.history.append(
        {"message": user_message, "is_user": True, "key": str(uuid.uuid4())}
    )

    st.session_state.history.append(
        {"message": result_text, "is_user": False, "key": str(uuid.uuid4())}
    )

    # get audio content as base 64
    audio_file = open(audio_filename, "rb")
    audio_data_binary = audio_file.read()
    audio_data = (base64.b64encode(audio_data_binary)).decode("ascii")

    st.session_state.history.append(
        {
            "message": "data:audio/mp3;base64," + audio_data,
            "is_user": False,
            "is_audio": True,
            "key": str(uuid.uuid4()),
        }
    )

    st.session_state.input_text = ""


# form
with st.form(key="my_form"):
    input_text = st.text_input("O que deseja?", key="input_text")
    submit_button = st.form_submit_button(label="Enviar", on_click=generate_answer)

# output
if st.session_state.history:
    for i in range(len(st.session_state["history"]) - 1, -1, -1):
        st_message(**st.session_state["history"][i])
