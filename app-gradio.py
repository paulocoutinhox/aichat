import os
import openai

import azure.cognitiveservices.speech as speechsdk
import gradio as gr


def form_submit(text_to_process):
    if not text_to_process:
        text_to_process = "me fale, em uma frase, algo sobre o james webb"

    # call openai api
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text_to_process,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.6,
    )

    result_text = response.choices[0].text

    if result_text:
        result_text = result_text.strip()

    # requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get("SPEECH_KEY"),
        region=os.environ.get("SPEECH_REGION"),
    )

    audio_config = speechsdk.audio.AudioOutputConfig(filename="audio.mp3")

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

    return ("audio.mp3", result_text)


# gradio interface
if __name__ == "__main__":
    gr.close_all()

    port = int(os.environ.get("PORT", 9000))
    text_to_process = gr.Textbox(
        label="Texto para processar",
        lines=5,
        value="principais lições do livro pai rico pai pobre em uma linha?",
    )

    outputs = [
        gr.Audio(label="Aúdio gerado"),
        gr.Label(label="Texto gerado"),
    ]

    demo = gr.Interface(fn=form_submit, inputs=text_to_process, outputs=outputs)
    demo.launch(server_port=port)
