import random
import schedule
import time
import fasttext
from sklearn.metrics.pairwise import cosine_similarity
import sys


def load_fasttext_model(file_path):
    model = fasttext.load_model(file_path)
    return model

# 모델 경로
fasttext_model = load_fasttext_model("cc.ko.300.bin")

# 단어 목록 파일에서 랜덤 단어 선택 함수
def get_random_word_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            words = f.readlines()
        random_word = random.choice(words).strip()  
        return random_word
    except Exception as e:
        print(f"단어 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

# 목표 단어 저장 함수
def save_random_word():
    random_word = get_random_word_from_file("assets/txt/word.txt")  
    if random_word:
        with open("target_word.txt", "w", encoding="utf-8") as f:
            f.write(random_word)
        print(f"선택된 단어: {random_word}")
    else:
        print("랜덤 단어를 선택하는 데 실패했습니다.")

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