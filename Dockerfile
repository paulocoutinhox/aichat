FROM python:3.10

USER root

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y build-essential libssl-dev libasound2 wget

RUN chgrp -R 0 /app \
    && chmod -R g=u /app \
    && pip install pip --upgrade \
    && pip install -r requirements.txt

# USE FOR GRADIO
# ENV GRADIO_SERVER_NAME="0.0.0.0"
# EXPOSE 9000
# CMD ["python3", "app-gradio.py"]

# USE FOR STREAMLIT
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app-streamlit.py"]
