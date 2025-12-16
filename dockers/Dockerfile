FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    pip install --no-cache-dir --user -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

FROM python:3.11-slim
WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

RUN mkdir -p /app/data /app/logs

COPY . /app

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DATABASE_PATH=/app/data/db.sqlite
ENV LOG_PATH=/app/logs/app.log

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
