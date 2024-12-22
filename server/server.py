from flask import Flask, render_template, request, jsonify
import random
import fasttext
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter

app = Flask(__name__)

def load_fasttext_model(file_path):
    model = fasttext.load_model(file_path)
    return model

fasttext_model = load_fasttext_model("cc.ko.300.bin")

def get_random_word_from_file(file_path):
    try:
        with open(file_path, "r", encoding = "utf-8") as f:
            words = f.readlines()
        random_word = random.choice(words).strip()
        return random_word
    except Exception as e:
        print(f"단어 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None
    