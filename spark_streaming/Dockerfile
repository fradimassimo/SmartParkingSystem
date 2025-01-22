FROM bitnami/spark:latest

WORKDIR /app

# Copy the PySpark application to the container
COPY spark_streaming.py /app/spark_streaming.py

COPY closed_lots.json /app/closed_lots.json

RUN pip3 install paho-mqtt

CMD ["spark-submit", "--master", "local[*]", "/app/spark_streaming.py"]
