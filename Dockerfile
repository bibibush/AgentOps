FROM python:3.13-slim
WORKDIR /app

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv
RUN uv pip install . --system --no-cache

EXPOSE 8000
CMD ["python", "main.py"]
