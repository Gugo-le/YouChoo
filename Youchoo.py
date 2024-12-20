import random
import schedule
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt
from gensim.models import Word2Vec

okt = Okt()

# 학습 모델 로드
def load_word2vec_model(file_path):
    model = Word2Vec.load(file_path)
    return model


word2vec_model = load_word2vec_model("word2vec_korean.model")

# 랜덤 단어 추출 함수
def get_random_word_from_word2vec():
    words_list = list(word2vec_model.wv.index_to_key)  
    random_word = random.choice(words_list) 
    return random_word

def save_random_word():
    random_word = get_random_word_from_word2vec()  
    with open("target_word.txt", "w", encoding="utf-8") as f:
        f.write(random_word)
    print(f"오늘의 단어가 '{random_word}'로 설정되었습니다. 게임을 시작하세요!")

schedule.every(24).hours.do(save_random_word)