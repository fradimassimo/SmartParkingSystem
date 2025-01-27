
FROM python:3.9-slim


WORKDIR /app

COPY ./consumer /app

RUN pip3 install paho-mqtt
RUN pip3 install psycopg2-binary

CMD ["python", "consumer.py"]
