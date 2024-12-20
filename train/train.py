import json
from konlpy.tag import Okt
from gensim.models import Word2Vec

# JSON 파일에서 문장 불러오기
with open('sentences.json', 'r', encoding='utf-8') as f:
    sentences = json.load(f)


okt = Okt()

def preprocess_sentence(sentence):
    
    tokens = okt.morphs(sentence)  
    # 불용어 제거 (필요에 따라 stopwords 추가)
    stopwords = ['이', '그', '저', '것', '들', '은', '는', '을', '를', '이', '가', '으로', '에서', '와', '한']
    tokens = [word for word in tokens if word not in stopwords]
    return tokens

# 각 문장을 형태소 분석하고 불용어를 제거한 후 학습용 데이터 준비
tokenized_sentences = [preprocess_sentence(sentence) for sentence in sentences]

model = Word2Vec(tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4)


model.save("word2vec_korean.model")
print("모델이 'word2vec_korean.model'로 저장되었습니다.")