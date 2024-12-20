import json
from konlpy.tag import Okt
from gensim.models import Word2Vec

# JSON 파일에서 문장 불러오기
with open('sentences.json', 'r', encoding='utf-8') as f:
    sentences = json.load(f)

def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        stopwords = [line.strip() for line in f.readlines()]
    return stopwords

# 불용어 목록 불러오기
stopwords = load_stopwords('stopwords-ko.txt')


okt = Okt()

# 문장 토큰화 (형태소 분석 및 불용어 제거)
def preprocess_sentence(sentence):
   
    tokens = okt.morphs(sentence)  
   
    tokens = [word for word in tokens if word not in stopwords]
    return tokens


tokenized_sentences = [preprocess_sentence(sentence) for sentence in sentences]


model = Word2Vec(tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4)


model.save("word2vec_korean.model")
print("모델이 'word2vec_korean.model'로 저장되었습니다.")