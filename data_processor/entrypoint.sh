#!/bin/bash
set -e  # Exit on error

echo "Starting cron service..."
cron

# Ensure the log file exists before tailing
touch /var/log/cron.log
echo "Cron log initialized at $(date)" >> /var/log/cron.log

echo "Running forecast_sarima.py..."
python /app/forecast_sarima.py &

# Keep the container running and monitoring the cron log
tail -f /var/log/cron.log
