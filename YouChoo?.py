import random
import schedule
import time
import fasttext
from sklearn.metrics.pairwise import cosine_similarity
import sys  

def load_fasttext_model(file_path):
    model = fasttext.load_model(file_path)
    return model


fasttext_model = load_fasttext_model("cc.ko.300.bin")


def save_random_word():
    
    random_word = "여기에서"  
    with open("target_word.txt", "w", encoding="utf-8") as f:
        f.write(random_word)

schedule.every(24).hours.do(save_random_word)

# 유사도 계산 함수
def calculate_similarity(user_word, target_word, model):
    try:
        user_vec = model.get_word_vector(user_word)  # 사용자 단어 벡터
        target_vec = model.get_word_vector(target_word)  # 목표 단어 벡터

        
        similarity = cosine_similarity([user_vec], [target_vec])
        return similarity[0][0]
    except Exception as e:
        print(f"단어 벡터 계산 중 오류가 발생했습니다: {e}")
        return None

# 유사도 계산 및 결과 출력
def check_word_guess(user_word, target_word, model):
    similarity_score = calculate_similarity(user_word, target_word, model)
    
    if similarity_score is None:
        return
    
    print(f"유사도 점수: {similarity_score * 100:.2f}%")
    
    if similarity_score == 1.0:  
        print(f"축하합니다! '{target_word}'를 맞추셨습니다!")
        sys.exit()  
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

    check_word_guess(user_input, target_word, fasttext_model)
    
    schedule.run_pending()
    time.sleep(1)