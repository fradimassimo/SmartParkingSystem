import pandas as pd
from datetime import datetime, timedelta
from forecast_sarima import get_festive_dates
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pickle
import psycopg2

def get_zone(lat, lon):
    zones = {
    "NORD": {
        "latitude": [46.10, 46.12],
        "longitude": [11.07, 11.14]
    },
    "SUD": {
        "latitude": [46.04, 46.06],
        "longitude": [11.07, 11.14]
    },
    "EST": {
        "latitude": [46.06, 46.10],
        "longitude": [11.11, 11.14]
    },
    "OVEST": {
        "latitude": [46.06, 46.10],
        "longitude": [11.07, 11.10]
    },
    "CENTRO": {
        "latitude": [46.06, 46.10],
        "longitude": [11.10, 11.11]
    }
    }

    for zone, coords in zones.items():
        lat_min, lat_max = coords["latitude"]
        lon_min, lon_max = coords["longitude"]
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return zone

def train_model(start_time = datetime.now(), end_time = None, festive_dates = None):

    if end_time is None:
        end_time = start_time - timedelta(days=28)
    elif end_time > start_time:
        raise ValueError("End time must be before start time")
    
    if festive_dates is None:
        festive_dates = get_festive_dates()

    # retrieve data from PostgreSQL
    pg_conn = psycopg2.connect(
    dbname="smart-parking",
    user="admin",
    password="root",
    host="postgres",
    port="5432"
    )

    df = pd.DataFrame()

    try:
        query = """
            SELECT o.*, p.latitude, p.longitude
            FROM occupancy_data o
            JOIN parkings p ON o.parking_id = p.parking_id
            WHERE o.timestamp BETWEEN %s AND %s
        """
        df = pd.read_sql(query, pg_conn, params=(end_time, start_time))

        if df.empty:
            print(f"No data found")      

    except Exception as e:
        print(f"Error retrieving parking data: {e}")

    finally:
        pg_conn.close()

    df.to_csv('out.csv')

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['zone'] = df.apply(lambda row: get_zone(row['latitude'], row['longitude']), axis=1)
    df.drop(columns=['latitude', 'longitude'], inplace=True)

    df['total_capacity'] = df['occupancy'] + df['vacancy']
    df['relative_occupancy'] = df['occupancy'] / df['total_capacity']
    # Round timestamps to the nearest hour
    df['rounded_timestamp'] = df['timestamp'].dt.floor('h')

    # Group by parking_id and rounded timestamp, then aggregate
    df_aggregated = df.groupby(['parking_id', 'rounded_timestamp'], as_index=False).agg(
        mean_occupancy=('relative_occupancy', 'mean')  # Aggregate occupancy
    )
    df_aggregated['zone'] = df.groupby(['parking_id', 'rounded_timestamp'])['zone'].transform('first')
    df_aggregated.rename(columns={'rounded_timestamp': 'timestamp'}, inplace=True)

    # Extract features
    df_aggregated['hour'] = df_aggregated['timestamp'].dt.hour
    df_aggregated['day_of_week'] = df_aggregated['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    df_aggregated['is_festive'] = df_aggregated['day_of_week'].apply(lambda x: 1 if x == 6 else 0)  # Sunday is festive

    df_aggregated['is_festive'] = df_aggregated['timestamp'].dt.date.isin(pd.to_datetime(festive_dates).date) | df_aggregated['is_festive']

    # Create dummies
    df_aggregated['zone'] = df_aggregated['zone'].astype(str) 
    parking_dummies = pd.get_dummies(df_aggregated['zone'], prefix='zone')
    df_aggregated = df_aggregated.join(parking_dummies).drop(columns=['zone', 'timestamp', 'parking_id'])
    

    # Rename occupancy to mean_occupancy
    df_aggregated.rename(columns={'occupancy': 'mean_occupancy'}, inplace=True)
    train_data = df_aggregated

    y_train = train_data['mean_occupancy']
    X_train = train_data.drop(columns=['mean_occupancy'])

    X_train = X_train.astype(int)
    X_train = X_train.apply(pd.to_numeric, errors='coerce').fillna(X_train.mean())

    # Fit SARIMA model
    sarima_model = SARIMAX(
        y_train,
        exog=X_train,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 24), # with daily seasonality
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    sarima_result = sarima_model.fit()
    print("Model created successfully")

    try:
        # Save the model using pickle
        with open("app/data_processor/sarima_model.pkl", "wb") as f:
            pickle.dump(sarima_result, f)
        print("Model saved successfully")
    except Exception as e:
        print(f"Error saving model: {e}")

def main():
    train_model()


if __name__ == "__main__":
    main()

