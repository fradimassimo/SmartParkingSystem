FROM bitnami/spark:latest

WORKDIR /app

COPY spark_streaming.py /app/spark_streaming.py

#si potrebbe cancellare
COPY 1766_sensors_data.json /app/1766_sensors_data.json

RUN pip3 install paho-mqtt

CMD ["spark-submit", "--master", "local[*]", "/app/spark_streaming.py"]
