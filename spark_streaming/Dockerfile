# Use OpenJDK 17 base image to ensure correct Java setup
FROM openjdk:17-slim

# Install Python and required dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME and PATH correctly
ENV JAVA_HOME=/usr/local/openjdk-17
ENV PATH=$JAVA_HOME/bin:$PATH

# Set working directory
WORKDIR /app

# Copy Python dependencies file and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy other project files
COPY utils.py .
COPY garage_parking.py .
COPY spark_streaming.py .
COPY entrypoint.sh .

# Ensure the entrypoint script is executable
RUN chmod +x entrypoint.sh

# Set entrypoint for the container
ENTRYPOINT ["/app/entrypoint.sh"]
