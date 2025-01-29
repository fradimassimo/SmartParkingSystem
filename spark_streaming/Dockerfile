FROM python:3.10-slim  

WORKDIR /app  

# Install Java (for Spark) and `ps`
RUN apt-get update && apt-get install -y openjdk-11-jdk procps && rm -rf /var/lib/apt/lists/*  

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  
ENV PATH="${JAVA_HOME}/bin:${PATH}"  

# Copy Spark dependencies (optional, if not using external Spark)
RUN wget -qO- https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz | tar xvz -C /opt/
ENV SPARK_HOME=/opt/spark  
ENV PATH="${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"  

COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt  

COPY entrypoint.sh .  
COPY garage_parking.py .  
COPY spark_streaming.py .  

RUN chmod +x entrypoint.sh  

CMD ["/bin/bash", "/app/entrypoint.sh"]
