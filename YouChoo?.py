import random
import schedule
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import FastText


def load_fasttext_model(file_path):
    model = FastText.load(file_path)
    return model


fasttext_model = load_fasttext_model("fasttext_korean.model")


def get_random_word_from_fasttext():
    words_list = list(fasttext_model.wv.index_to_key) 
    random_word = random.choice(words_list)  
    return random_word


def save_random_word():
    random_word = get_random_word_from_fasttext() 
    with open("target_word.txt", "w", encoding="utf-8") as f:
        f.write(random_word)  
    


schedule.every(24).hours.do(save_random_word)

# 유사도 계산 함수
def calculate_similarity(user_word, target_word, fasttext_model):
    
    user_vec = fasttext_model.wv[user_word]
    target_vec = fasttext_model.wv[target_word]

    
    similarity = cosine_similarity([user_vec], [target_vec])
    return similarity[0][0]


def check_word_guess(user_word, target_word, fasttext_model):
    try:
        similarity_score = calculate_similarity(user_word, target_word, fasttext_model)
        print(f"유사도 점수: {similarity_score * 100:.2f}%")

        if similarity_score == 1.0:  
            print(f"축하합니다! '{target_word}'를 맞추셨습니다!")
        else:
            print(f"아직 아닙니다. '{user_word}'와 목표 단어의 의미가 조금 다릅니다. 계속 도전해보세요!")
    except KeyError as e:
        print(f"단어 '{e.args[0]}'가 모델에 없습니다. 다른 단어를 입력해 주세요.")


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
    

    check_word_guess(user_input, target_word, fasttext_model)
    
    
    schedule.run_pending()
    time.sleep(1)