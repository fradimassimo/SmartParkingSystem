FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
# RUN apt-get update && apt-get install -y netcat-openbsd

EXPOSE 5000

CMD ["python", "fraui.py"]
