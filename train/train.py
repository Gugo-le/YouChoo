import json
from konlpy.tag import Okt
from gensim.models import Word2Vec

# JSON 파일에서 문장 불러오기
with open('sentences.json', 'r', encoding='utf-8') as f:
    sentences = json.load(f)

okt = Okt()

tokenized_sentences = [okt.morphs(sentence) for sentence in sentences]
model = Word2Vec(tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4)
model.save("word2vec_korean.model")

vector = model.wv['자연어']
print(vector)

similar_words = model.wv.most_similar('자연어', topn=5)
print(similar_words)