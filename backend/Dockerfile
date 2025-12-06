FROM python:3.11-slim AS production

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    postgresql-client \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN adduser --system --group app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/storage && \
    chmod +x /app/scripts/*.sh 2>/dev/null || true && \
    chown -R app:app /app

USER app

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips "*"
