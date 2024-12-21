from gensim.models import FastText

# FastText 모델 로드 함수
def load_fasttext_model(model_path):
    try:
        model = FastText.load_model(model_path)
        print("FastText 모델 로드 성공!")
        return model
    except FastText.FastText._FastTextException as e:
        print(f"FastText 로딩 오류: {e}")
    except FileNotFoundError as e:
        print(f"모델 파일을 찾을 수 없습니다: {e}")
    except Exception as e:
        print(f"기타 오류: {e}")
    return None

# 모델 경로
model_path = 'cc.ko.300.bin'  # 한국어 FastText 모델 경로

# 모델 로드
fasttext_model = load_fasttext_model(model_path)

if fasttext_model:
    # 모델이 성공적으로 로드된 경우
    print("모델이 로드되었습니다.")
else:
    print("모델 로드 실패.")