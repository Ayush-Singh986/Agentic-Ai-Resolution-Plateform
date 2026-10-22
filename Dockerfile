FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/huggingface

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

# Bake the sentence-transformer weights and matching FAISS metadata into the image.
RUN python ingest_data.py

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app /opt/huggingface

USER appuser

EXPOSE 8000 8501

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
