import time
import random
import fasttext
import io
import base64
import threading
import datetime
import redis
from wordcloud import WordCloud
from operator import itemgetter
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify, render_template, session


app = Flask(__name__)
app.secret_key = 'strawberrycake'

redis_client = redis.StrictRedis(host='localhost', port=6379, db = 0, decode_responses=True)

# FastText 모델 로드
def load_fasttext_model(file_path):
    try:
        model = fasttext.load_model(file_path)
        return model
    except Exception as e:
        print(f"FastText 모델 로드 중 오류: {e}")
        return None

fasttext_model = load_fasttext_model("cc.ko.300.bin")

# 매일 랜덤 목표 단어 생성
def get_daily_target_word(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            words = f.readlines()
        today = datetime.date.today()
        random.seed(today.toordinal())
        return random.choice(words).strip()
    except Exception as e:
        print(f"목표 단어 생성 중 오류: {e}")
        return None

# 유사도 계산 함수
def calculate_similarity(user_word, target_word, model):
    try:
        user_vec = model.get_word_vector(user_word)
        target_vec = model.get_word_vector(target_word)
        similarity = cosine_similarity([user_vec], [target_vec])
        return similarity[0][0]
    except Exception as e:
        print(f"유사도 계산 중 오류: {e}")
        return None
   

# 워드클라우드 생성
def generate_wordcloud_base64():
    try:
        with open("all_words.txt", "r", encoding="utf-8") as f:
            words = f.readlines()

        word_counts = Counter([word.strip() for word in words])
        wordcloud = WordCloud(
            font_path="assets/fonts/Do_Hyeon/DoHyeon-Regular.ttf",
            width=800,
            height=400,
            background_color="white"
        ).generate_from_frequencies(word_counts)

        img = io.BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()
    except Exception as e:
        print(f"워드클라우드 생성 중 오류: {e}")
        return None


def daily_reset():
    global rankings, attempts, game_over
    
    target_word = get_daily_target_word("assets/txt/word.txt")
    if target_word:
        with open("target_word.txt", "w", encoding = "utf-8") as f:
            f.write(target_word)
        print("목표 단어가 초기화되었습니다.")    
        
    img_base64 = generate_wordcloud_base64()
    if img_base64:
        with open("wordcloud_base64.txt", "w", encoding="utf-8") as f:
            f.write(img_base64)
        print("어제의 워드클라우드가 초기화되었습니다.")
        
    rankings = []
    attempts = 0
    game_over = False            

# 랭킹 업데이트
def update_and_get_rankings(user_word, similarity_score, rankings):
    for i, (word, score) in enumerate(rankings):
        if word == user_word:
            if similarity_score > score:
                rankings[i] = (user_word, similarity_score)
            break
    else:
        rankings.append((user_word, similarity_score))

    rankings.sort(key=lambda x: x[1], reverse=True)
    return next((i + 1 for i, (word, _) in enumerate(rankings) if word == user_word), len(rankings))

# 워드클라우드 주기적 업데이트
def update_wordcloud_periodically():
    while True:
        try:
            img_base64 = generate_wordcloud_base64()
            if img_base64:
                with open("wordcloud_base64.txt", "w", encoding="utf-8") as f:
                    f.write(img_base64)
        except Exception as e:
            print(f"워드클라우드 업데이트 오류: {e}")
        time.sleep(60)

# 전역 상태 변수
rankings = []
attempts = 0
game_over = False

# 기본 페이지
@app.route('/')
def index():
    return render_template('index.html')

# 게임 상태 확인
@app.route('/check-status', methods=['GET'])
def check_status():
    user_status = session.get("game_status")
    if user_status == "finished":
        return jsonify({"status": "finished"})
    return jsonify({"status": "new"})

# 게임 시작
@app.route('/start', methods=['GET'])
def start_game():
    global game_over, attempts
    game_over = False
    attempts = 0

    target_word = get_daily_target_word("assets/txt/word.txt")
    if target_word:
        with open("target_word.txt", "w", encoding="utf-8") as f:
            f.write(target_word)
        session["game_status"] = "new"
        return jsonify({"message": "게임이 시작되었습니다."}), 200
    return jsonify({"error": "목표 단어를 생성하지 못했습니다."}), 500

# 단어 추측
@app.route('/guess', methods=['POST'])
def guess():
    global game_over, attempts, rankings

    data = request.get_json()
    user_input = data.get("user_input", "").strip()

    if not user_input:
        return jsonify({"error": "단어를 입력하세요."}), 400

    with open("target_word.txt", "r", encoding="utf-8") as f:
        target_word = f.read().strip()

    # 정답 확인
    if user_input == target_word:
        game_over = True
        session["game_status"] = "finished"
        return jsonify({
            "message": target_word,
            "attempts": attempts + 1,
            "rankings": rankings
        }), 200

    # 유사도 계산
    similarity_score = calculate_similarity(user_input, target_word, fasttext_model)
    if similarity_score is None:
        return jsonify({"error": "유사도 계산에 실패했습니다."}), 500

    # float32 -> float 변환
    similarity_score = float(similarity_score)

    attempts += 1
    rank = update_and_get_rankings(user_input, similarity_score, rankings)

    # 입력 단어 기록
    with open("all_words.txt", "a", encoding="utf-8") as f:
        f.write(user_input + "\n")

    return jsonify({
        "user_input": user_input,
        "similarity_score": similarity_score,
        "rank": rank,
        "attempts": attempts
    }), 200

# 포기
@app.route('/giveup', methods=['GET'])
def giveup():
    global game_over
    game_over = True
    with open("target_word.txt", "r", encoding="utf-8") as f:
        target_word = f.read().strip()

    session["game_status"] = "finished"
    return jsonify({"message": target_word})

# 워드클라우드 반환
@app.route('/wordcloud', methods=['GET'])
def wordcloud():
    try:
        with open("wordcloud_base64.txt", "r", encoding="utf-8") as f:
            img_base64 = f.read().strip()
        return jsonify({"wordcloud": img_base64}), 200
    except Exception as e:
        print(f"워드클라우드 반환 오류: {e}")
        return jsonify({"error": "워드클라우드를 가져올 수 없습니다."}), 500

# 사용자들 텍스트와 그에 맞는 랭킹 저장
@app.route('/submit', methods=['POST'])
def submit_text():
    data = request.get_json()
    user_input = data.get("text", "").strip()
    similarity = data.get("similarity", 0.0)
    
    if not user_input:
        return jsonify({"error": "텍스트를 입력하세요."}), 400
    try:
        redis_client.zadd("text_rankings", {user_input: similarity})
        return jsonify({"message": "텍스트가 저장되었습니다."}), 200
    except Exception as e:
        return jsonify({"error": f"저장 중 오류 발생: {str(e)}"}), 500
 
# 랭킹 조회
@app.route('/rankings', methods=['GET'])
def get_rankings():
    try:
        # Redis에서 랭킹 데이터 조회
        rankings = redis_client.zrevrange("text_rankings", 0, 9, withscores=True)
        formatted_rankings = [
            {"rank": idx + 1, "text": text, "similarity": round(score, 2)}
            for idx, (text, score) in enumerate(rankings)
        ]
        return jsonify({"rankings": formatted_rankings}), 200
    except Exception as e:
        return jsonify({"error": f"랭킹 조회 중 오류 발생: {str(e)}"}), 500

# 워드클라우드 업데이트 스레드 시작
if __name__ == '__main__':
    threading.Thread(target=update_wordcloud_periodically, daemon=True).start()
    app.run(debug=True)