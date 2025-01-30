FROM python:3.10-slim

WORKDIR /app

# Copy necessary files
COPY train_sarima.py .
COPY forecast_sarima.py .
COPY utils.py .
COPY requirements.txt . 

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Schedule train_sarima.py to run daily at 22:00
RUN echo "0 22 * * * python /app/train_sarima.py >> /var/log/cron.log 2>&1" > /etc/cron.d/sarima_cron
RUN chmod 0644 /etc/cron.d/sarima_cron
RUN crontab /etc/cron.d/sarima_cron

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Start both cron and forecast_sarima.py at container startup
CMD ["/app/entrypoint.sh"]