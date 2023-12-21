from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os, shutil
from zipfile import ZipFile
import librosa
import torch
from audio_splitter import split_audio_file
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from dotenv import load_dotenv

load_dotenv()
runtime_env = os.getenv("RUNTIME_ENV")
# base_api_url = "http://127.0.0.1" if runtime_env == "production" else "http://localhost"
base_api_url = "http://127.0.0.1"

app = Flask(__name__)
CORS(
    app,
    # resources={r"/start_transcription_job/*": {"origins": f"{base_api_url}:5000"}},
)

# app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

cache_dir = "./Model/"
model_name = "openai/whisper-large-v3"
device = "cuda" if torch.cuda.is_available() else "cpu"

model = WhisperForConditionalGeneration.from_pretrained(
    model_name, cache_dir=cache_dir + model_name + "model"
).to(device)

processor = WhisperProcessor.from_pretrained(
    model_name, cache_dir=cache_dir + model_name + "processor"
)

print("Model loaded successfully! \n")


#! Functions - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def transcribe_file(audio_file_path):
    # Load the audio file
    speech_data, sr = librosa.load(audio_file_path)

    inputs = processor.feature_extractor(
        speech_data, return_tensors="pt", sampling_rate=16_000
    ).input_features.to(device)
    forced_decoder_ids = processor.get_decoder_prompt_ids(
        language="he", task="transcribe"
    )

    predicted_ids = model.generate(
        inputs, max_length=480_000, forced_decoder_ids=forced_decoder_ids
    )
    result = processor.tokenizer.batch_decode(
        predicted_ids, skip_special_tokens=True, normalize=True
    )[0]

    print("TRANSCRIBING... | Result is: ", result[::-1])
    return result


def batch_transcribe(file_list, speaker):
    conversation = []
    for i, file in enumerate(file_list):
        transcript = transcribe_file(file["file"])
        time = file["time"]
        conversation.append(
            {"text": transcript, "start_time": time, "speaker": speaker}
        )
    return conversation


def format_full_transcript(transcript):
    full_text = ""

    for i, item in enumerate(transcript):
        full_text += "\n\n" + item["speaker"] + ":\n" + item["text"]

    with open("TranscriptResult.txt", "w", encoding="utf-8") as file:
        file.write(full_text)

    return full_text


#! Routes - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route("/start_transcription_job", methods=["POST"])
def start_transcription_job():
    print("Transcription job started...")
    # app.logger.log(0, "Started request to ModelEndpoint...")
    # app.logger.log(0, request.files)
    # try:
    uploaded_file = request.files["zip_file"]
    if not uploaded_file:
        return jsonify({"message": "Error at Transcription Service"})

    print("FILE IS: ", uploaded_file)
    zipfile = "audio_files.zip"
    extracted_folder_path = "audio_files"

    # if os.listdir(extracted_folder_path).__len__() != 0:
    #     shutil.rmtree(extracted_folder_path)

    os.makedirs(extracted_folder_path, exist_ok=True)

    with open(zipfile, "wb") as f:
        f.write(uploaded_file.read())
    with ZipFile(zipfile, "r") as zip_ref:
        zip_ref.extractall(extracted_folder_path)

    file_list = os.listdir(extracted_folder_path)
    print("File List is: ", file_list)

    sp_audio_list = split_audio_file("audio_files/" + file_list[0], 900, -40, 1200, -20)
    bc_audio_list = split_audio_file("audio_files/" + file_list[1], 900, -40, 1200, -20)

    sp_transcript = batch_transcribe(sp_audio_list, "ServicePerson")
    bc_transcript = batch_transcribe(bc_audio_list, "BusinessClient")

    full_transcript = sp_transcript + bc_transcript
    sorted_transcript = sorted(full_transcript, key=lambda x: x["start_time"])

    # response = requests.post(
    #     f"{base_api_url}:5000/on_transcription_work_finished/",
    #     json={"fullTranscript": sorted_transcript},
    # )
    return jsonify({"fullTranscript": sorted_transcript})

    # except Exception as e:
    #     # response = requests.get(f"{base_api_url}:5000/on_transcription_work_failed/")
    #     # print("Error at Transcription Service: ", e)
    #     return jsonify({"message": "Error at Transcription Service"})

    # return jsonify({"fullTranscript": sorted_transcript})


@app.route("/test", methods=["GET"])
def test_front():
    return jsonify("Model Service Communication!!!! OK")


@app.route("/post-test", methods=["POST"])
def test_post():
    csd = request.get_json()
    print("Got JSON!")
    return jsonify(csd)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)
