import random
import schedule
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Kkma
from gensim.models import Word2Vec

kkma = Kkma()


def load_word2vec_model(file_path):
    model = Word2Vec.load(file_path)
    return model


word2vec_model = load_word2vec_model("word2vec_korean.model")

def get_random_word_from_word2vec():
    words_list = list(word2vec_model.wv.index_to_key)  
    random_word = random.choice(words_list) 
    return random_word


def save_random_word():
    random_word = get_random_word_from_word2vec()  
    with open("target_word.txt", "w", encoding="utf-8") as f:
        f.write(random_word)


schedule.every(24).hours.do(save_random_word)

# 유사도 계산 함수
def calculate_similarity(user_word, target_word, word2vec_model):
    
    if user_word not in word2vec_model.wv:
        print(f"모델에 '{user_word}' 단어가 없습니다. 다른 단어를 입력해 주세요.")
        return None

    if target_word not in word2vec_model.wv:
        print(f"목표 단어 '{target_word}'가 모델에 없습니다. 다시 설정해 주세요.")
        return None

    
    user_vec = word2vec_model.wv[user_word]
    target_vec = word2vec_model.wv[target_word]

   
    similarity = cosine_similarity([user_vec], [target_vec])
    return similarity[0][0]

def check_word_guess(user_word, target_word, word2vec_model):
    similarity_score = calculate_similarity(user_word, target_word, word2vec_model)
    
    # 유사도 점수 없을 경우 예외 처리
    if similarity_score is None:
        return
    
    print(f"유사도 점수: {similarity_score * 100:.2f}%")
    
    if similarity_score == 1.0:  
        print(f"축하합니다! '{target_word}'를 맞추셨습니다!")
    else:
        print(f"아직 아닙니다. '{user_word}'와 목표 단어의 의미가 조금 다릅니다. 계속 도전해보세요!")

# 초기 랜덤 단어 저장
save_random_word()


while True:
    user_input = input("단어를 입력하세요('포기하기'를 입력하면 정답을 알려드립니다): ")
    
    if user_input == "포기하기":
        with open("target_word.txt", "r", encoding="utf-8") as f:
            target_word = f.read().strip()
        print(f"정답은 '{target_word}'입니다.")
        break
    
    if user_input == "q": 
        break
    
    
    with open("target_word.txt", "r", encoding="utf-8") as f:
        target_word = f.read().strip()
    
    
    check_word_guess(user_input, target_word, word2vec_model)
    
    
    schedule.run_pending()
    time.sleep(1)