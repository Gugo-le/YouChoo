from konlpy.tag import Okt
okt = Okt()
text = "학교도 안 가는데 프로젝트나 하나 해볼까?"

morphs = okt.morphs(text)
print(morphs)