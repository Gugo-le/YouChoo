from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter


with open("first_words.txt", "r", encoding="utf-8") as f:
    words = f.readlines()

words = [word.strip() for word in words]
word_counts = Counter(words)  


wordcloud = WordCloud(font_path="assets/fonts/Do_Hyeon/DoHyeon-Regular.ttf", width=800, height=400, background_color="white").generate_from_frequencies(word_counts)


plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()