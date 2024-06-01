from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
from transformers import AutoTokenizer, AutoModel
import torch
import fire
from openai import OpenAI

# from interact_llama3_llamacpp import interact
import spacy

nlp = spacy.load("ru_core_news_lg")

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")
app = FastAPI()


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask


# tokenizer = AutoTokenizer.from_pretrained("ai-forever/sbert_large_nlu_ru")
# model = AutoModel.from_pretrained("ai-forever/sbert_large_nlu_ru")
import pandas as pd

data = pd.read_csv('clear_data.csv')
sentences = data['title'].tolist()
sentences2 = data['description'].fillna('нет').tolist()
linkss = data['url'].tolist()
# encoded_input = tokenizer(sentences, padding=True, truncation=True, max_length=512, return_tensors='pt')
# with torch.no_grad():
#     model_output = model(**encoded_input)
# sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
sentence_embeddings = []
for i in range(len(sentences)):
    sentence_embeddings.append(nlp(sentences[i]))


class Request(BaseModel):
    query: str


class Response(BaseModel):
    text: str
    links: List[str]


class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: List[ValidationError]


@app.exception_handler(HTTPException)
async def validation_exception_handler(request, exc):
    return HTTPValidationError(detail=[
        ValidationError(loc=[], msg=str(exc.detail), type="value_error")
    ])


SYSTEM_PROMPT = "Ты — Сайга, русскоязычный автоматический ассистент. Ты работаешь в Тинькофф в отделе Бизнес и помощь и помогаешь предпринимателям с ведением бизнеса. Все, что спрашивают про финансы, банк, бизнесс, инвестиции - это про Тинькофф. Ты не должен отвечать на вопросы, которые не относятся к темам про финансы, банк, бизнесс, инвестиции. Если спросят про другие темы, то ответь, что это не твоя область знаний."


@app.post("/assist")
async def assist(request: Request):
    to_find = request.query
    hist = [{"role": "system", "content": SYSTEM_PROMPT}]
    # encoded_input = tokenizer(to_find, padding=True, truncation=True, max_length=512, return_tensors='pt')
    # # Compute token embeddings
    # with torch.no_grad():
    #     model_output = model(**encoded_input)
    # Perform pooling. In this case, mean pooling
    # to_find_imb = mean_pooling(model_output, encoded_input['attention_mask'])
    to_find_imb = nlp(to_find)
    d = []
    # + (to_find_imb @ sentence_embeddings2[i]).item()
    for i in range(0, len(sentences)):
        # d.append([(to_find_imb @ sentence_embeddings[i]).item(), sentences[i], linkss[i]])
        d.append([to_find_imb.similarity(sentence_embeddings[i]), sentences[i], linkss[i], i])
    d.sort(reverse=True)
    if d[0][0] < 0.88:
        hist.append({"role": "user", "content": to_find})
        completion = client.chat.completions.create(
            model="local-model",
            messages=hist,
            temperature=0.4,
        )
        content = completion.choices[0].message.content
    else:
        content = sentences2[d[0][3]]
    # text = str(fire.Fire(interact('model-q4_K.gguf', messages=hist)))
    links = [d[0][2], d[1][2], d[2][2]]
    return Response(text=content, links=links)
