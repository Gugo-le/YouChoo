import random
import schedule
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt
from gensim.models import Word2Vec