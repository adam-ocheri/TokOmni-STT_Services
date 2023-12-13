from flask import Flask, send_file, jsonify, request
import requests
from zipfile import ZipFile
import boto3
import os
from dotenv import load_dotenv
from storage_access import S3Client
from audio_utils import AudioSource
from db_connection import PostgresController
from speechbrain.pretrained import SpectralMaskEnhancement
from flask_cors import CORS
from file_utils import generate_presigned_url, upload_file_to_s3, download_audio_file

from dotenv import load_dotenv

load_dotenv()
aws_bucket = os.getenv("AWS_S3_BUCKET_NAME")
aws_access_key = os.getenv("AWS_S3_ACCESS_KEY")
aws_secret_access_key = os.getenv("AWS_S3_SECRET_ACCESS_KEY")

# s3_client = S3Client(aws_bucket, aws_access_key, aws_secret_access_key)

aws_access_key_id = aws_access_key
aws_secret_access_key = aws_secret_access_key
region_name = "eu-central-1"
bucket_name = aws_bucket

# Create an S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
)

db = PostgresController()

nr_model = SpectralMaskEnhancement.from_hparams(
    "speechbrain/metricgan-plus-voicebank",
    savedir="pretrained_models/metricgan-plus-voicebank",
)

app = Flask(__name__)
CORS(
    app,
    resources={r"/request_transcription_work/*": {"origins": "http://localhost:3000"}},
)


@app.route("/request_transcription_work/<path:filename>", methods=["GET"])
def request_transcription_work(filename):
    # Create presigned link for filename
    print("Requested transcription work...")
    if db.working_id != -1:
        return jsonify({"message": "Error! transcriptor is already working"}), 500

    db.on_transcription_requested()

    stereo_file_url = generate_presigned_url(s3_client, bucket_name, filename)
    print("STEREO FILE URL: ", stereo_file_url)
    # Download audio file
    download_audio_file(stereo_file_url, filename)

    conversation = AudioSource(nr_model, filename)  # Split stereo file to 2 mono files

    zip_file_path = "compressed-audio.zip"
    with ZipFile(zip_file_path, "w") as zip_file:
        zip_file.write(
            conversation.audio_channel__service_person,
            os.path.basename(conversation.audio_channel__service_person),
        )
        zip_file.write(
            conversation.audio_channel__business_client,
            os.path.basename(conversation.audio_channel__business_client),
        )

    # Send the zip file to another server
    model_service_url = "http://localhost:8080/start_transcription_job"  # Replace with the actual URL of the other server
    files = {"zip_file": open(zip_file_path, "rb")}
    response = requests.post(model_service_url, files=files)

    # Check the response from the other server
    if response.status_code == 200:
        transcript = response.json().get("fullTranscript")
        return jsonify({"fullTranscript": transcript})
    else:
        return jsonify({"message": "Error sending file to the other server"}), 500


@app.route("/on_transcription_work_finished/", methods=["POST"])
def on_transcription_work_finished():
    response = request.get_json()
    transcript = response.get("fullTranscript")
    print("Full Transcript Obtained:\n", transcript)
    db.on_transcription_finished(transcript)
    return jsonify({})


@app.route("/on_transcription_work_failed/", methods=["GET"])
def on_transcription_work_failed():
    db.on_transcription_failed()
    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True)
