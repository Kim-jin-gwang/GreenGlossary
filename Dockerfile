# GreenGlossary — 산림·농업 전문용어 순화 Flask 서버
# tensorflow-text는 Windows 휠이 없어 로컬(Windows)에서는 모델 추론이 불가능했는데,
# 이 이미지(Linux)로는 어디서든 동일하게 실행/검증할 수 있다.
# 실행: docker build -t greenglossary . && docker run -p 5000:5000 greenglossary
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=5000

# KoNLPy(Okt)가 JVM을 요구한다
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt huggingface_hub

COPY . .

# KoBERT 모델(~1.3GB)은 GitHub에 없음 — 기동 시 HF 모델 저장소에서 자동 다운로드
EXPOSE 5000
CMD ["sh", "-c", "python download_models.py && python server.py"]
