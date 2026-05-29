# Multi-stage build — non-root user, no baked secrets
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS production
COPY . .
ENV ANTHROPIC_API_KEY="" PORT=8080
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser /app
USER appuser
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
