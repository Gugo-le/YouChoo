FROM python:3.10-slim


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


WORKDIR /app


COPY . /app


RUN pip install --upgrade pip
RUN pip install -r requirements.txt


CMD ["flask", "run", "--host=0.0.0.0"]