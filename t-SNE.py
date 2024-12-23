import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

# 무작위 단어 생성함
word_embeddings = np.random.rand(100, 300)  
words = [f"word{i}" for i in range(100)]


tsne = TSNE(n_components=2, random_state=42)
word_embeddings_2d = tsne.fit_transform(word_embeddings)


plt.figure(figsize=(10, 10))
for i, word in enumerate(words):
    plt.scatter(word_embeddings_2d[i, 0], word_embeddings_2d[i, 1])
    plt.annotate(word, (word_embeddings_2d[i, 0], word_embeddings_2d[i, 1]), fontsize=9)
plt.xlabel('t-SNE 1')
plt.ylabel('t-SNE 2')
plt.title('t-SNE Visualization of Word Embeddings')
plt.grid(True)
plt.show()