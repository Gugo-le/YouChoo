import random
import schedule
import time
import fasttext
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

def load_fasttext_model(file_path):
    """FastText 모델 로드."""
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


def update_and_get_rankings(user_word, similarity_score, rankings):
    """랭킹 업데이트 및 현재 단어의 순위 반환."""
    for i, (word, score) in enumerate(rankings):
        if word == user_word:
            if similarity_score > score:
                rankings[i] = (user_word, similarity_score)
            break
    else:
        rankings.append((user_word, similarity_score))

    rankings.sort(key=lambda x: x[1], reverse=True)
    rank = next((i + 1 for i, (word, _) in enumerate(rankings) if word == user_word), len(rankings))
    return rank


def display_top_rankings(rankings, top_n=30):
    """Top N 랭킹 출력."""
    print(f"\n🏆 Top {top_n} Rankings 🏆")
    for i, (word, score) in enumerate(rankings[:top_n], start=1):
        print(f"{i}. {word} - 유사도: {score * 100:.2f}%")

# 하... 개 같네요
def check_word_guess(user_word, target_word, model, rankings):
    """사용자 입력 단어를 점검."""
    # 문자열이 완전히 동일한지 먼저 확인
    if user_word.strip() == target_word.strip():
        print(f"축하합니다! '{target_word}'를 맞추셨습니다!")
        return True, 1.0, 1  # 유사도 1.0, 랭킹 1위로 반환

    # 유사도 계산
    similarity_score = calculate_similarity(user_word, target_word, model)
    if similarity_score is None:
        return False, None, None

    # 랭킹 업데이트
    rank = update_and_get_rankings(user_word, similarity_score, rankings)
    print(f"'{user_word}'의 유사도 점수: {similarity_score * 100:.2f}% | 랭킹: {rank}위")

    # 유사도가 1.0인 경우 정답 처리
    if abs(similarity_score - 1.0) < 1e-6:
        print(f"축하합니다! '{target_word}'를 맞추셨습니다!")
        return True, similarity_score, rank
    else:
        return False, similarity_score, rank
    
def wordcloud():
    with open("first_words.txt", "r", encoding= "utf-8") as f:
        words = f.readlines()
        
    words = [word.strip() for word in words]
    word_counts = Counter(words)
    
    wordcloud = WordCloud(font_path="assets/fonts/Do_Hyeon/DoHyeon-Regular.ttf", width=800, height=400, background_color="white").generate_from_frequencies(word_counts)   

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

save_random_word()

attempts = 0  
rankings = []  
first_words = []  

game_over = False

while True:
    user_input = input("단어를 입력하세요('포기하기'를 입력하면 정답을 알려드립니다): ")

    
    if attempts == 0:
        first_words.append(user_input)
        with open("first_words.txt", "a", encoding="utf-8") as f:
            f.write(user_input + "\n")

   
    if user_input == "포기하기":
        with open("target_word.txt", "r", encoding="utf-8") as f:
            target_word = f.read().strip()
        print(f"정답은 '{target_word}'입니다.")
        print(f"총 도전 횟수: {attempts}번")
        break

    if user_input == "q":
        print(f"게임을 종료합니다. 총 도전 횟수: {attempts}번")
        break

        
    if user_input == "워드클라우드":
        wordcloud()
        continue
    
    if game_over:
        print("사용자들의 첫 단어 빈도 수가 궁금하시면 '워드클라우드'를 입력해주세요.")
        
        
    with open("target_word.txt", "r", encoding="utf-8") as f:
        target_word = f.read().strip()

    attempts += 1
    guessed_correctly, similarity_score, rank = check_word_guess(user_input, target_word, fasttext_model, rankings)

   
    if guessed_correctly:
        print(f"총 도전 횟수: {attempts}번")
        display_top_rankings(rankings)
        game_over = True
        continue

    schedule.run_pending()
    time.sleep(1)