import spacy
import pandas as pd

data = pd.read_csv('clear_data.csv')
sentences = data['title'].tolist()
sentences2 = data['description'].fillna('нет').tolist()
linkss = data['url'].tolist()
nlp = spacy.load("ru_core_news_lg")
sentence_embeddings = []
for i in range(len(sentences)):
    sentence_embeddings.append(nlp(sentences[i]))


def get_sim(word):
    to_find_imb = nlp(word)
    d = []
    for i in range(0, len(sentences)):
        d.append([to_find_imb.similarity(sentence_embeddings[i]), sentences[i], linkss[i], i, sentences2[i]])
    d.sort(reverse=True)
    return d[:3]
