FROM python:3.10-slim

WORKDIR /app

COPY check_parkings.py .
COPY processed_data_generator.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# we use cron to schedule the script to run every 8 hours (check for new parkings)
RUN apt-get update && apt-get install -y cron

RUN echo "0 */8 * * * python /app/check_parkings.py >> /var/log/cron.log 2>&1" > /etc/cron.d/parkings_cron
RUN chmod 0644 /etc/cron.d/parkings_cron
RUN crontab /etc/cron.d/parkings_cron

# also run check_parkings.py immediately when the container starts
CMD ["sh", "-c", "python /app/check_parkings.py && cron -f"]