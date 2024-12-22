from flask import Flask, render_template, request, jsonify
import random
import fasttext
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter