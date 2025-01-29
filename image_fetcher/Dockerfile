FROM python:3.10-slim

WORKDIR /app

COPY ./image_fetcher /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
