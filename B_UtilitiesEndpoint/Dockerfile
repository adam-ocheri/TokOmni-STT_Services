FROM python:3.11.4

ENV RUNTIME_ENV=production

WORKDIR /

RUN apt-get update && \
    apt-get install -y ffmpeg

COPY requirements.txt /
COPY .env /
RUN pip install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /
COPY audio_utils.py /
COPY db_connection.py /
COPY storage_access.py /
COPY file_utils.py /
COPY audio_cache /
COPY audio_processed /
COPY app.py /

EXPOSE 5000


CMD ["python", "app.py"]