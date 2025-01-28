FROM python:3.10-slim

WORKDIR /app

COPY train_sarima.py .
COPY forecast_sarima.py .
COPY utils.py .
COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

# we use cron to schedule the script to run every day at 10pm
RUN apt-get update && apt-get install -y cron

RUN echo "0 22 * * * python /app/train_sarima.py >> /var/log/cron.log 2>&1" > /etc/cron.d/sarima_cron
RUN chmod 0644 /etc/cron.d/sarima_cron
RUN crontab /etc/cron.d/sarima_cron

CMD ["cron", "-f"]