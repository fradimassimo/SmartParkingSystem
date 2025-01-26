from pymongo import MongoClient
import psycopg2

# first we fetch data from mongo
mongo_client = MongoClient("mongodb://mongodb:27017/")
mongo_db = mongo_client["parking_management"] 
mongo_parkings = mongo_db["parkings"]

parking_data = list(mongo_parkings.find({}, {"_id": 0}))  

# then we export data from postgres if necessary (i.e. if there are differences in data)

# connect to PostgreSQL
pg_conn = psycopg2.connect(
    dbname="smart-parking",
    user="admin",
    password="root",
    host="postgres",
    port="5432"
)
pg_cur = pg_conn.cursor()

 # we periodically check if the data in PostgreSQL is up-to-date with the data in MongoDB (i.e. if new entries have been added)
for parking in parking_data:
        pg_cur.execute("SELECT * FROM parkings WHERE parking_id = %s", (str(parking["parking_id"]),))
        result = pg_cur.fetchone()

        if not result: # insert parking
            try:
                pg_cur.execute(
                    """
                    INSERT INTO parkings (parking_id, name, latitude, longitude, paying_hours, price_per_hour, parking_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        parking["parking_id"],
                        parking["name"],
                        parking["location"]["latitude"],
                        parking["location"]["longitude"],
                        parking["paying_hours"],
                        parking["price_per_hour"],
                        "street"
                    )
                )
            except Exception as e:
                print(f"Error inserting parking {parking['parking_id']}: {e}")
        else:
            pass    

pg_conn.commit()
pg_cur.close()
pg_conn.close()

print("Parking data successfully transferred from MongoDB to PostgreSQL.")


