import json
from konlpy.tag import Okt


sentences = [
    "나는 자연어 처리 모델을 학습하고 있습니다.",
    "Word2Vec은 단어 벡터화를 위한 모델입니다.",
    "한국어는 형태소 기반 언어입니다."
]

with open('sentences.json', 'w', encoding='utf-8') as f:
    json.dump(sentences, f, ensure_ascii=False, indent=4)