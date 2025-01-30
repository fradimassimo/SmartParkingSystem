FROM python:3.10-slim

WORKDIR /app


COPY mongo/populate_mongo.py .
COPY mongo/requirements.txt .
COPY data_generation /app/data_generation
COPY mongo/_annotations.coco.json /app/mongo/_annotations.coco.json
COPY mongo/new_parking_handling.py .

RUN pip install -r requirements.txt
