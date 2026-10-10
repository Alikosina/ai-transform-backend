FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from langchain_community.embeddings import FastEmbedEmbeddings; FastEmbedEmbeddings(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

COPY app ./app

EXPOSE 3001

# В проде Nginx проксирует /api -> backend; локально без прокси задайте ROOT_PATH= в .env
ENV ROOT_PATH=/api

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 3001 --root-path \"$ROOT_PATH\""]
