FROM python:3.11.4

ENV RUNTIME_ENV=production

WORKDIR /

COPY requirements.txt /
COPY app.py /
COPY audio_utils.py /
COPY db_connection.py /
COPY storage_access.py /
COPY file_utils.py /
COPY audio_cache /
COPY audio_processed /
COPY app.py /

# torch==2.0.1+cu117
# torchaudio==2.0.2+cu117

RUN pip install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
RUN pip install --no-cache-dir -r requirements.txt

# RUN pip install huggingface-hub python-dotenv

EXPOSE 5000

CMD ["python", "app.py"]