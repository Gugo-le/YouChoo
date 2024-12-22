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

def get_random_word_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            words = f.readlines()
        random_word = random.choice(words).strip()
        return random_word
    except Exception as e:
        print(f"단어 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

def save_random_word():
    random_word = get_random_word_from_file("assets/txt/word.txt")
    if random_word:
        with open("target_word.txt", "w", encoding="utf-8") as f:
            f.write(random_word)
    else:
        print("랜덤 단어를 선택하는 데 실패했습니다.")

schedule.every(24).hours.do(save_random_word)

def calculate_similarity(user_word, target_word, model):
    try:
        user_vec = model.get_word_vector(user_word)
        target_vec = model.get_word_vector(target_word)
        similarity = cosine_similarity([user_vec], [target_vec])
        return similarity[0][0]
    except Exception as e:
        print(f"단어 벡터 계산 중 오류가 발생했습니다: {e}")
        return None

def check_word_guess(user_word, target_word, model, attempts):
    similarity_score = calculate_similarity(user_word, target_word, model)
    
    if similarity_score is None:
        return attempts
    
    print(f"'{user_word}'의 유사도 점수: {similarity_score * 100:.2f}%")
    
    if similarity_score == 1.0:
        print(f"축하합니다! '{target_word}'를 맞추셨습니다!")
        print(f"총 도전 횟수: {attempts}번")
        sys.exit()
    else:
        print(f"'{user_word}'와/과 목표 단어의 의미가 조금 다릅니다. 계속 도전해보세요!")
    
    return attempts + 1

save_random_word()
attempts = 0

while True:
    user_input = input("단어를 입력하세요('포기하기'를 입력하면 정답을 알려드립니다): ")
    
    if user_input == "포기하기":
        with open("target_word.txt", "r", encoding="utf-8") as f:
            target_word = f.read().strip()
        print(f"정답은 '{target_word}'입니다.")
        print(f"총 도전 횟수: {attempts}번")
        break
    
    if user_input == "q":
        print(f"게임을 종료합니다. 총 도전 횟수: {attempts}번")
        break
    
    with open("target_word.txt", "r", encoding="utf-8") as f:
        target_word = f.read().strip()

    attempts = check_word_guess(user_input, target_word, fasttext_model, attempts)
    
    schedule.run_pending()
    time.sleep(1)