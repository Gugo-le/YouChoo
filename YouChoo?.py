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

def check_word_guess(user_word, target_word, model):
    similarity_score = calculate_similarity(user_word, target_word, model)
    if similarity_score is None:
        return False, None
    
    print(f"#{attempts} '{user_word}'의 유사도 점수: {similarity_score * 100:.2f}% | 랭킹: {rankings}")
    
    if similarity_score == 1.0:
        print(f"축하합니다! '{target_word}'를 맞추셨습니다!")
        return True, similarity_score
    else:
        return False, similarity_score

def display_rankings(rankings):
    print("\n📊 현재 랭킹:")
    sorted_rankings = sorted(rankings, key=lambda x: x[1], reverse=True)
    for i, (word, score) in enumerate(sorted_rankings[:5], 1):  # 상위 5개만 표시
        print(f"{i}. {word} - 유사도: {score * 100:.2f}%")
    print()

save_random_word()
attempts = 0
rankings = []

while True:
    user_input = input("단어를 입력하세요('포기하기'를 입력하면 정답을 알려드립니다): ")
    
    if user_input == "포기하기":
        with open("target_word.txt", "r", encoding="utf-8") as f:
            target_word = f.read().strip()
        print(f"정답은 '{target_word}'입니다.")
        print(f"총 도전 횟수: {attempts}번")
        display_rankings(rankings)
        break
    
    if user_input == "q":
        print(f"게임을 종료합니다. 총 도전 횟수: {attempts}번")
        display_rankings(rankings)
        break
    
    with open("target_word.txt", "r", encoding="utf-8") as f:
        target_word = f.read().strip()
    
    attempts += 1
    guessed_correctly, similarity_score = check_word_guess(user_input, target_word, fasttext_model)
    
    if similarity_score is not None: # is 연산자 호출 -> 좌/우 같은지 확인
        rankings.append((user_input, similarity_score))  # 단어와 유사도를 기록
        display_rankings(rankings)  # 현재 랭킹 표시
    
    if guessed_correctly:
        print(f"총 도전 횟수: {attempts}번")
        break
    
    schedule.run_pending()
    time.sleep(1)