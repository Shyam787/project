FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .
RUN python -c "from sentence_transformers import CrossEncoder, SentenceTransformer; SentenceTransformer('BAAI/bge-m3'); CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)"

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
