import time
import schedule
import random
import fasttext
import io
import os
import base64
import threading
import datetime
import uuid
import redis
try:
    from gensim.models import FastText as GensimFastText
except Exception:
    GensimFastText = None
from wordcloud import WordCloud
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify, render_template, session
from flask.cli import AppGroup

app = Flask(__name__)
app.secret_key = 'strawberrycake'

# 현재 작업 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# 사용자 고유 ID 생성
@app.before_request
def ensure_user_id():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
        
# FastText 모델 로드
def load_fasttext_model(file_path):
    if not os.path.exists(file_path):
        print(f"경고: FastText 모델 파일을 찾을 수 없습니다: {file_path}")
        print("FastText 모델을 다운로드하려면 다음 명령어를 실행하세요:")
        print("wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/cc.ko.300.bin -P project/model/")
        return None
    try:
        model = fasttext.load_model(file_path)
        return model
    except Exception as e:
        print(f"FastText 모델 로드 중 오류: {e}")
        return None

fasttext_model = load_fasttext_model("project/model/cc.ko.300.bin")

# gensim FastText 모델(증분 학습용) 로드
def load_gensim_model(file_path):
    if GensimFastText is None:
        print("경고: gensim이 설치되어 있지 않아 gensim FastText를 사용할 수 없습니다.")
        return None
    if not os.path.exists(file_path):
        return None
    try:
        model = GensimFastText.load(file_path)
        print(f"Loaded gensim model: {file_path}")
        return model
    except Exception as e:
        print(f"gensim FastText 모델 로드 중 오류: {e}")
        return None

gensim_model = load_gensim_model("project/model/gensim_fasttext.model")

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
def calculate_similarity(user_word, target_word, model=None):
    """Calculate cosine similarity between two words.
    Preference order:
      1) gensim_model (if available and contains the word)
      2) fasttext_model (facebook fasttext)
    """
    try:
        # try gensim model first (incremental updates live here)
        if gensim_model is not None:
            try:
                user_vec = gensim_model.wv[user_word]
                target_vec = gensim_model.wv[target_word]
                similarity = cosine_similarity([user_vec], [target_vec])
                return float(similarity[0][0])
            except KeyError:
                # missing in gensim model, fallback to fasttext
                pass

        # fallback to fasttext model
        if model is not None:
            try:
                user_vec = model.get_word_vector(user_word)
                target_vec = model.get_word_vector(target_word)
                similarity = cosine_similarity([user_vec], [target_vec])
                return float(similarity[0][0])
            except Exception:
                pass

        print("경고: 유사도 계산에 사용할 수 있는 모델이 없습니다. 기본값 0.5 반환")
        return 0.5
    except Exception as e:
        print(f"유사도 계산 중 오류: {e}")
        return 0.5

# 워드클라우드 생성
def generate_wordcloud_base64():
    try:
        with open("project/txt/all_words.txt", "r", encoding="utf-8") as f:
            words = f.readlines()

        word_counts = Counter([word.strip() for word in words])
        wordcloud = WordCloud(
            font_path="project/static/fonts/Do_Hyeon/DoHyeon-Regular.ttf",
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

# 랭킹, 목표 단어, 워드클라우드 초기화
def daily_reset():
    global rankings, attempts, game_over
    
    target_word = get_daily_target_word("project/txt/word.txt")
    if target_word:
        with open("project/txt/target_word.txt", "w", encoding="utf-8") as f:
            f.write(target_word)
        print("목표 단어가 초기화되었습니다.")    
        
    img_base64 = generate_wordcloud_base64()
    if img_base64:
        with open("project/txt/wordcloud_base64.txt", "w", encoding="utf-8") as f:
            f.write(img_base64)
        print("어제의 워드클라우드가 초기화되었습니다.")
        
    # 랭킹 초기화
    redis_client.delete("correct_users")
    print("랭킹이 초기화되었습니다.")
    
    # 모든 사용자 세션 초기화
    with app.app_context():
        for key in list(session.keys()):
            session.pop(key)
        print("모든 사용자 세션이 초기화되었습니다.")
    
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
                with open("project/txt/wordcloud_base64.txt", "w", encoding="utf-8") as f:
                    f.write(img_base64)
        except Exception as e:
            print(f"워드클라우드 업데이트 오류: {e}")
        time.sleep(5)
        
# 워드클라우드 오전 12시 초기화
def reset_all_words():
    try:
        with open("project/txt/wordcloud_base64.txt", "w", encoding="utf-8") as f:
            f.write("")
        print("wordcloud_base64.txt 파일이 초기화되었습니다.")
        
        with open("project/txt/all_words.txt", "w", encoding="utf-8") as f:
            f.write("")
        print("모든 단어가 초기화되었습니다.")
    except Exception as e:
        print(f"wordcloud_base64.txt 초기화 중 오류: {e}")  
        
schedule.every().day.at("00:00").do(reset_all_words)
schedule.every().day.at("00:00").do(daily_reset)

# 5초마다 예약된 작업 있는지 확인 후 오전 12시 되면 함수 실행
def schedule_jobs():
    while True:
        schedule.run_pending()
        time.sleep(5)                  

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


# 닉네임 설정 엔드포인트
@app.route('/set-nickname', methods=['POST'])
def set_nickname():
    try:
        data = request.get_json()
        nickname = (data.get('nickname') or '').strip()
        if not nickname:
            return jsonify({'error': '닉네임을 입력해주세요.'}), 400
        if len(nickname) > 20:
            return jsonify({'error': '닉네임은 20자 이하로 입력해주세요.'}), 400

        user_id = session.get('user_id')
        if not user_id:
            # 보통 @before_request에서 생성되지만 안전장치
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id

        # 세션과 Redis에 닉네임 저장
        session['nickname'] = nickname
        try:
            redis_client.hset(f"user:{user_id}", "nickname", nickname)
        except Exception as e:
            print(f"Redis에 닉네임 저장 중 오류: {e}")

        return jsonify({'nickname': nickname}), 200
    except Exception as e:
        print(f"닉네임 설정 중 오류: {e}")
        return jsonify({'error': '닉네임 설정 중 오류가 발생했습니다.'}), 500

# 정답 맞춘 사용자 정보 저장
def save_correct_user(user_id, user_word, attempts, time_taken):
    try:
        attempts = float(attempts)
        redis_key = f"{user_id}:{user_word}"
        redis_client.zadd("correct_users", {redis_key: attempts})
        redis_client.hset(redis_key, "time_taken", time_taken)
        print(f"정답 사용자 {user_id} 저장 완료: {user_word}, 시도 횟수: {attempts}, 걸린 시간: {time_taken}")
    except Exception as e:
        print(f"정답 사용자 저장 중 오류: {e}")

# 정답 맞춘 사용자 랭킹 조회
def get_correct_user_rank(user_id, user_word):
    try:
        redis_key = f"{user_id}:{user_word}"
        rank = redis_client.zrank("correct_users", redis_key)
        if rank is not None:
            return rank + 1
        return None
    except Exception as e:
        print(f"정답 사용자 랭킹 조회 중 오류: {e}")
        return None

# 게임 시작
@app.route('/start', methods=['GET'])
def start_game():
    global game_over, attempts
    game_over = False
    attempts = 0

    target_word = get_daily_target_word("project/txt/word.txt")
    if target_word:
        with open("project/txt/target_word.txt", "w", encoding="utf-8") as f:
            f.write(target_word)
        session["game_status"] = "new"
        session["start_time"] = datetime.datetime.now(datetime.timezone.utc)
        return jsonify({"message": "게임이 시작되었습니다."}), 200
    return jsonify({"error": "목표 단어를 생성하지 못했습니다."}), 500

# 단어 추측
@app.route('/guess', methods=['POST'])
def guess():
    global game_over, attempts, rankings

    data = request.get_json()
    user_input = data.get("user_input", "").strip()
    user_id = session.get("user_id")

    if not user_input:
        return jsonify({"error": "단어를 입력하세요."}), 400

    with open("project/txt/target_word.txt", "r", encoding="utf-8") as f:
        target_word = f.read().strip()

    # 정답 확인
    if user_input == target_word:
        game_over = True
        session["game_status"] = "finished"
        start_time = session.get("start_time")
        end_time = datetime.datetime.now(datetime.timezone.utc)
        time_taken_seconds = (end_time - start_time).total_seconds()
        minutes, seconds = divmod(time_taken_seconds, 60)
        time_taken = f"{int(minutes)}분 {int(seconds)}초"
        save_correct_user(user_id, user_input, attempts + 1, time_taken)
        rank = get_correct_user_rank(user_id, user_input)
        user_message = f"🎉 축하합니다. {attempts + 1}번째 만에 정답을 맞췄습니다! 랭킹은 {rank}위 입니다. 걸린 시간: {time_taken}"
        return jsonify({
            "message": target_word,
            "attempts": attempts + 1,
            "rankings": rankings,
            "rank": rank,
            "user_message": user_message
        }), 200

    # 유사도 계산
    similarity_score = calculate_similarity(user_input, target_word, fasttext_model)
    if similarity_score is None:
        return jsonify({"error": "유사도 계산에 실패했습니다."}), 500

    similarity_score = float(similarity_score)

    attempts += 1
    rank = update_and_get_rankings(user_input, similarity_score, rankings)

    with open("project/txt/all_words.txt", "a", encoding="utf-8") as f:
        f.write(user_input + "\n")

    return jsonify({
        "user_input": user_input,
        "similarity_score": similarity_score,
        "rank": rank,
        "attempts": attempts
    }), 200

# 포기: 정답 반환, 세션 정보 업데이트
@app.route('/giveup', methods=['GET'])
def giveup():
    global game_over
    game_over = True
    with open("project/txt/target_word.txt", "r", encoding="utf-8") as f:
        target_word = f.read().strip()

    session["game_status"] = "finished"
    return jsonify({"message": target_word})

# 워드클라우드 반환
@app.route('/wordcloud', methods=['GET'])
def wordcloud():
    try:
        with open("project/txt/wordcloud_base64.txt", "r", encoding="utf-8") as f:
            img_base64 = f.read().strip()
        return jsonify({"wordcloud": img_base64}), 200
    except Exception as e:
        print(f"워드클라우드 반환 오류: {e}")
        return jsonify({"error": "워드클라우드를 가져올 수 없습니다."}), 500

# 워드클라우드 api
@app.route('/wordcloud', methods=['GET'])
def get_wordcloud():
    try:
        with open("project/txt/wordcloud_base64.txt", "r", encoding="utf-8") as f:
            wordcloud_base64 = f.read()
        return jsonify({"wordcloud_base64": wordcloud_base64}), 200
    except Exception as e:
        print(f"워드클라우드 반환 중 오류: {e}")
        return jsonify({"error": "워드클라우드를 반환하지 못했습니다."}), 500


# Health check endpoint for CI/CD
@app.route('/health', methods=['GET'])
def health_check():
    status = {}
    ok = True
    # time
    status['time'] = datetime.datetime.utcnow().isoformat() + 'Z'
    # target word file check
    try:
        if os.path.exists("project/txt/target_word.txt"):
            status['target_word_file'] = 'ok'
        else:
            status['target_word_file'] = 'missing'
            ok = False
    except Exception as e:
        status['target_word_file'] = f'error: {str(e)}'
        ok = False

    # redis check
    try:
        redis_client.ping()
        status['redis'] = 'ok'
    except Exception as e:
        status['redis'] = f'error: {str(e)}'
        ok = False

    status['status'] = 'ok' if ok else 'fail'
    return (jsonify(status), 200) if ok else (jsonify(status), 500)
    
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

# TOP 10 랭킹 조회
@app.route('/top10', methods=['GET'])
def top10():
    try:
        rankings = redis_client.zrange("correct_users", 0, 9, withscores=True)
        formatted_rankings = []
        for key, score in rankings:
            time_taken = redis_client.hget(key, "time_taken")
            uuid_full = key.split(":")[0]
            uuid_short = uuid_full[:8] + "..." + uuid_full[-8:]
            # 닉네임이 있으면 불러오기
            nickname = None
            try:
                nickname = redis_client.hget(f"user:{uuid_full}", "nickname")
            except Exception:
                nickname = None
            formatted_rankings.append({
                "uuid": uuid_short,
                "nickname": nickname,
                "word": key.split(":")[1],
                "attempts": score,
                "time": time_taken
            })
        formatted_rankings.sort(key=lambda x: x["attempts"])
        return jsonify({"rankings": formatted_rankings}), 200
    except Exception as e:
        return jsonify({"error": f"TOP 10 랭킹 조회 중 오류 발생: {str(e)}"}), 500

# Flask 커맨드 그룹 생성
cli = AppGroup('custom')

# target_word 출력 명령어 추가
@cli.command('show-target-word')
def show_target_word():
    try:
        with open("project/txt/target_word.txt", "r", encoding="utf-8") as f:
            target_word = f.read().strip()
        print(f"오늘의 정답 단어는: {target_word}")
    except Exception as e:
        print(f"정답 단어를 읽는 중 오류 발생: {e}")

# Redis 데이터베이스 출력 명령어 추가
@cli.command('show-redis-data')
def show_redis_data():
    try:
        keys = redis_client.keys('*')
        if not keys:
            print("Redis 데이터베이스가 비어 있습니다.")
            return

        for key in keys:
            value = redis_client.get(key)
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Redis 데이터베이스를 읽는 중 오류 발생: {e}")

app.cli.add_command(cli)

if __name__ == '__main__':
    threading.Thread(target=update_wordcloud_periodically, daemon=True).start()
    threading.Thread(target=schedule_jobs, daemon=True).start()
    app.run(debug=True)