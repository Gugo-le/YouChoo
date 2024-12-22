from flask import Flask, request, jsonify, render_template
import random
import fasttext
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud
import io
import base64
from collections import Counter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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


def calculate_similarity(user_word, target_word, model):
    try:
        user_vec = model.get_word_vector(user_word)
        target_vec = model.get_word_vector(target_word)
        similarity = cosine_similarity([user_vec], [target_vec])
        return similarity[0][0]
    except Exception as e:
        print(f"단어 벡터 계산 중 오류가 발생했습니다: {e}")
        return None


def generate_wordcloud_base64():
    with open("first_words.txt", "r", encoding="utf-8") as f:
        words = f.readlines()

    words = [word.strip() for word in words]
    word_counts = Counter(words)

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


rankings = []
attempts = 0
game_over = False


@app.route('/start', methods=['GET'])
def start_game():
    global game_over, attempts
    game_over = False
    attempts = 0

    random_word = get_random_word_from_file("assets/txt/word.txt")
    if random_word:
        with open("target_word.txt", "w", encoding="utf-8") as f:
            f.write(random_word)
        return jsonify({"message": "게임이 시작되었습니다."}), 200
    return jsonify({"error": "랜덤 단어를 생성하지 못했습니다."}), 500

@app.route('/guess', methods=['POST'])
def guess():
    global game_over, attempts, rankings

    data = request.get_json()
    user_input = data.get("user_input", "").strip()

    if not user_input:
        return jsonify({"error": "입력된 단어가 없습니다."}), 400

    with open("target_word.txt", "r", encoding="utf-8") as f:
        target_word = f.read().strip()

    if user_input == target_word:
        game_over = True
        return jsonify({
            "message": "축하합니다! 정답입니다!",
            "attempts": attempts + 1,
            "rankings": rankings
        }), 200

    similarity_score = calculate_similarity(user_input, target_word, fasttext_model)
    if similarity_score is None:
        return jsonify({"error": "유사도 계산에 실패했습니다."}), 500

    # JSON 직렬화가 가능하도록 float으로 변환
    similarity_score = float(similarity_score)

    attempts += 1
    rank = update_and_get_rankings(user_input, similarity_score, rankings)

    return jsonify({
        "user_input": user_input,
        "similarity_score": similarity_score,
        "rank": rank,
        "attempts": attempts
    }), 200

    similarity_score = calculate_similarity(user_input, target_word, fasttext_model)
    if similarity_score is None:
        return jsonify({"error": "유사도 계산에 실패했습니다."}), 500

    attempts += 1
    rank = update_and_get_rankings(user_input, similarity_score, rankings)

    return jsonify({
        "user_input": user_input,
        "similarity_score": similarity_score,
        "rank": rank,
        "attempts": attempts
    }), 200

@app.route('/wordcloud', methods=['GET'])
def wordcloud():
    try:
        img_base64 = generate_wordcloud_base64()
        return jsonify({"wordcloud": img_base64}), 200
    except Exception as e:
        print(f"워드클라우드 생성 중 오류가 발생했습니다: {e}")
        return jsonify({"error": "워드클라우드를 생성하지 못했습니다."}), 500


def update_and_get_rankings(user_word, similarity_score, rankings):
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

if __name__ == '__main__':
    app.run(debug=True)