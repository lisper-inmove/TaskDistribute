# FROM mh.com:8890/test/task-distribute:v1.0
FROM mh.com:8890/test/fastapi-base:v1.0

WORKDIR /app

ENV API_VERESION=v1.0 \
    APPROOT=/app/src \
    MQ_TYPE=REDIS \
    PYTHONPATH=/app:/app/src

COPY . .

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
