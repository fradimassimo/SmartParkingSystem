FROM python:3.10-slim

WORKDIR /app

COPY check_parkings.py .
COPY processed_data_generator.py .
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "check_parkings.py"]

