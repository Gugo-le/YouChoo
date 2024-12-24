import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import fasttext
import numpy as np
import random
import matplotlib.font_manager as fm


font_path = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'  # MacOS의 경우
font_prop = fm.FontProperties(fname=font_path)
plt.rc('font', family=font_prop.get_name())


def load_fasttext_model(file_path):
    try:
        model = fasttext.load_model(file_path)
        return model
    except Exception as e:
        print(f"FastText 모델 로드 중 오류: {e}")
        return None

# 단어 벡터 추출
def get_word_vectors(words, model):
    vectors = []
    for word in words:
        vectors.append(model.get_word_vector(word))
    return np.array(vectors) 


def plot_tsne(words, vectors, target_word, user_word):
    # PCA로 차원 축소
    pca = PCA(n_components=50)
    pca_result = pca.fit_transform(vectors)

    tsne = TSNE(n_components=2, random_state=0, perplexity=5, n_iter=300)
    tsne_results = tsne.fit_transform(pca_result)

    plt.figure(figsize=(16, 10))
    for i, word in enumerate(words):
        if word == target_word:
            color = 'red'
            alpha = 1.0
            size = 300
            plt.scatter(tsne_results[i, 0], tsne_results[i, 1], color=color, alpha=alpha, s=size)
            plt.annotate(word, (tsne_results[i, 0], tsne_results[i, 1]), fontsize=12, alpha=alpha, fontproperties=font_prop)
        elif word == user_word:
            color = 'blue'
            alpha = 1.0
            size = 300
            plt.scatter(tsne_results[i, 0], tsne_results[i, 1], color=color, alpha=alpha, s=size)
            plt.annotate(word, (tsne_results[i, 0], tsne_results[i, 1]), fontsize=12, alpha=alpha, fontproperties=font_prop)
        else:
            color = 'black'
            alpha = 0.2  
            size = 30
            plt.scatter(tsne_results[i, 0], tsne_results[i, 1], color=color, alpha=alpha, s=size)
    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.title('t-SNE Visualization of Words')
    plt.show()

# 단어 리스트 로드
def load_words(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            words = f.read().splitlines()
        return words
    except Exception as e:
        print(f"단어 리스트 로드 중 오류: {e}")
        return []


words = load_words("assets/txt/word.txt")
fasttext_model = load_fasttext_model("cc.ko.300.bin")
target_word = random.choice(words)


user_word = input("단어를 입력하세요: ").strip()
words.append(user_word)


word_vectors = get_word_vectors(words, fasttext_model)
plot_tsne(words, word_vectors, target_word, user_word)