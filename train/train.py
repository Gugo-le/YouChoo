import json
from konlpy.tag import Kkma
from gensim.models import FastText

# JSON 파일에서 문장 불러오기
with open('sentences.json', 'r', encoding='utf-8') as f:
    sentences = json.load(f)


def load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        stopwords = [line.strip() for line in f.readlines()]
    return stopwords


stopwords = load_stopwords('stopwords-ko.txt')

kkma = Kkma()

# 문장 전처리 함수 (형태소 분석 및 불용어 제거)
def preprocess_sentence(sentence):
    tokens = kkma.morphs(sentence)  
    tokens = [word for word in tokens if word not in stopwords] 
    return tokens

# 문장 데이터 전처리
tokenized_sentences = [preprocess_sentence(sentence) for sentence in sentences]

# FastText 모델 학습
model = FastText(
    tokenized_sentences, 
    vector_size=100,  
    window=5,         
    min_count=1,     
    workers=4         
)

model.save("fasttext_korean.model")
print("FastText 모델이 'fasttext_korean.model'로 저장되었습니다.")