FROM python:3.10-slim

WORKDIR /app

COPY ./image_fetcher/parking_occupancy.py .
COPY ./image_fetcher/weights.pt .
COPY ./image_fetcher/requirements.txt .
COPY ./parking_detection/models /app/parking_detection/models
COPY ./parking_detection/utils /app/parking_detection/utils

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
