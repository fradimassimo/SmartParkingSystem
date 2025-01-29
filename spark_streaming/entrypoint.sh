#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Checking if parking data exists in PostgreSQL..."
DB_CHECK=$(python -c "
import psycopg2
conn = psycopg2.connect(dbname='smart-parking', user='admin', password='root', host='postgres', port='5432')
cur = conn.cursor()
cur.execute(\"SELECT COUNT(*) FROM parkings WHERE parking_type = 'garage';\")
count = cur.fetchone()[0]
conn.close()
print(count)
")

if [ "$DB_CHECK" -eq "0" ]; then
    echo "No parking data found. Running garage_parking.py..."
    python garage_parking.py
else
    echo "Parking data already exists. Skipping database population."
fi

echo "Starting Spark Streaming..."
exec spark-submit --master local[*] /app/spark_streaming.py
