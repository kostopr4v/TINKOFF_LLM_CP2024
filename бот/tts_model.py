from TTS.api import TTS
import torch

tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

def text2speech(text, file_path):
    text = text.split('Подробнее: \nhttps://')[0]
    print(text)
    tts_model.tts_to_file(text=text,
                file_path=file_path,
                speaker_wav="путин.mp3",
                language="ru")