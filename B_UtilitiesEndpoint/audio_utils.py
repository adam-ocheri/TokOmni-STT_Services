from pydub import AudioSegment
import torch
import torchaudio
import os
from pathlib import Path

# Set the path to the ffmpeg binary
# environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"
# AudioSegment.converter = (
#     r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe"
# )
# AudioSegment.converter = "/usr/bin/ffmpeg"


class AudioUtils:
    @staticmethod
    def __save_audio(sound: AudioSegment, save_as: Path):
        print("Trying to save file... (EXPORT...)")
        sound.export(save_as.__str__())

    @staticmethod
    def convert_mp3_to_wav(mp3_file: Path) -> Path:
        # Create a new file path for the WAV file
        wav_file = mp3_file.with_suffix(".wav")

        # Load the MP3 file and export it as WAV
        sound = AudioSegment.from_mp3(mp3_file.__str__())
        sound.export(wav_file.__str__(), format="wav")

        return wav_file

    @staticmethod
    def split_audio_file_to_mono_files(
        file_to_split: Path, destination_folder: Path, nr_model
    ):
        wavefile = AudioUtils.convert_mp3_to_wav(file_to_split)
        audio_to_split = AudioSegment.from_file(wavefile)
        file_paths = []
        for index, channel in enumerate(audio_to_split.split_to_mono()):
            original_file_name = wavefile.stem
            file_type = wavefile.suffix
            subfolder = "/ServicePerson" if index == 0 else "/BusinessClient"
            save_mono_as_file = f"{destination_folder}/{subfolder}/{original_file_name}_NR_chn{index}{file_type}"
            enhance_mono_audio(
                nr_model, original_file_name + file_type, save_mono_as_file
            )
            AudioUtils.__save_audio(channel, save_mono_as_file)
            file_paths.append(save_mono_as_file)
        return file_paths


class AudioSource:
    def __init__(self, nr_model, filename=None):
        self.audio_channel__service_person = None
        self.audio_channel__business_client = None
        print("TRYING TO INITIALIZE AUDIO SOURCE.........................\n")
        if filename is not None:
            self.filename = Path(filename)
        else:
            self.filename = ""

        self.directory = Path("audio_processed")

        if filename is not None:
            self.separate_speakers_in_stereo_file(nr_model=nr_model)

    def separate_speakers_in_stereo_file(self, filename=None, nr_model=None):
        if filename is not None:
            self.filename = filename

        audio_files = AudioUtils.split_audio_file_to_mono_files(
            self.filename, self.directory, nr_model
        )

        print("AUDIO FILES: ", audio_files)
        print("Audio Files: ", audio_files[0], audio_files[1])

        self.audio_channel__service_person = audio_files[0]
        self.audio_channel__business_client = audio_files[1]


def enhance_mono_audio(nr_model, filename, output):
    # Load and add fake batch dimension
    noisy = nr_model.load_audio(filename).unsqueeze(0)

    # Add relative length tensor
    enhanced = nr_model.enhance_batch(noisy, lengths=torch.tensor([1.0]))

    # Saving enhanced signal on disk
    torchaudio.save(output, enhanced.cpu(), 16000)
