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