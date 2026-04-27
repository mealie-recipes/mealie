FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV MINIO_BUCKET=mlflow-artifacts
ENV TAG_VECTOR_CANDIDATES=production/tag_to_vector.pkl,canary/tag_to_vector.pkl,staging/tag_to_vector.pkl

COPY serving/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY serving /app/serving

EXPOSE 8000

CMD ["uvicorn", "serving.main:app", "--host", "0.0.0.0", "--port", "8000"]
