# 베이스 이미지로 Python 3.10 사용
FROM python:3.10-slim

# 시스템 종속성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libomp-dev \
    mecab \
    mecab-ipadic \
    git \
    curl \
    xz-utils \
    file \
    sudo \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 프로젝트 파일 복사
COPY . /app

# 필요한 패키지 설치
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Flask 애플리케이션 실행
CMD ["flask", "run", "--host=0.0.0.0"]