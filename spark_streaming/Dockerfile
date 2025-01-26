FROM bitnami/spark:latest

WORKDIR /app

COPY spark_streaming.py /app/spark_streaming.py
COPY utils.py /app/utils.py
COPY 1766_sensors_data.json /app/1766_sensors_data.json
COPY closed_parking_structures.json /app/closed_parking_structures.json

RUN pip3 install paho-mqtt

CMD ["spark-submit", "--master", "local[*]", "/app/spark_streaming.py"]
