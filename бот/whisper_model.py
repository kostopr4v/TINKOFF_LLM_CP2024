import stable_whisper
import csv
import ssl
import os
import torch
ssl._create_default_https_context = ssl._create_unverified_context

model = stable_whisper.load_model('large-v3')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    result.to_tsv(audio_path.split('.')[0] + '.tsv')
    text = ''
    tsv_file = open(audio_path.split('.')[0] + '.tsv', 'r+', encoding='utf-8')
    read_tsv = csv.reader(tsv_file, delimiter="\t")
    for row in read_tsv:
        if len(row) > 0:
            text += f' {row[-1]}'
    
    os.remove(audio_path)
    os.remove(audio_path.split('.')[0] + '.tsv')
    
    return text
