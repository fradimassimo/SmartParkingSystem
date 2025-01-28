FROM bitnami/spark:latest

WORKDIR /app

COPY spark_streaming.py /app/spark_streaming.py
COPY utils.py /app/utils.py
COPY 1766_sensors_data.json /app/1766_sensors_data.json
COPY corrected_closed_parking_structures.json /app/corrected_closed_parking_structures.json
COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["spark-submit", "--master", "local[*]", "/app/spark_streaming.py"]
