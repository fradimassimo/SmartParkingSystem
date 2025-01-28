import pandas as pd
from datetime import datetime, timedelta
from forecast_sarima import get_festive_dates
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sqlalchemy import create_engine
import pickle
import sys

def get_zone(lat, lon):
    zones = {
        "NORD": {"latitude": [46.100001, 46.12], "longitude": [11.070001, 11.14]},
        "SUD": {"latitude": [46.04, 46.06], "longitude": [11.0070001, 11.14]},
        "EST": {"latitude": [46.060001, 46.10], "longitude": [11.110001, 11.14]},
        "OVEST": {"latitude": [46.060001, 46.10], "longitude": [11.070001, 11.10]},
        "CENTRO": {"latitude": [46.060001, 46.10], "longitude": [11.100001, 11.11]},
    }

    for zone, coords in zones.items():
        lat_min, lat_max = coords["latitude"]
        lon_min, lon_max = coords["longitude"]
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return zone

def train_model(start_time=datetime.now(), end_time=None, festive_dates=None):
    if end_time is None:
        end_time = start_time - timedelta(days=28)
    elif end_time > start_time:
        raise ValueError("End time must be before start time")
    
    if festive_dates is None:
        festive_dates = get_festive_dates()

    # Replace with your actual PostgreSQL connection details
    DATABASE_URI = "postgresql://admin:root@postgres:5432/smart-parking"
    engine = create_engine(DATABASE_URI)

    try:
        # Retrieve data from PostgreSQL
        query = """
            SELECT o.*, p.latitude, p.longitude,  p.parking_type
            FROM occupancy_data o
            JOIN parkings p ON o.parking_id = p.parking_id
            WHERE o.timestamp BETWEEN %(end_time)s AND %(start_time)s
            AND o.parking_id = '2'
        """
        print("Fetching data from the database...")
        df = pd.read_sql(query, engine, params={"end_time": end_time, "start_time": start_time})

        if df.empty:
            print("No data found.")
            return

        print("Data fetched successfully.")

    except Exception as e:
        print(f"Error retrieving parking data: {e}", file=sys.stderr)
        return


    # Preprocess data
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['zone'] = df.apply(lambda row: get_zone(row['latitude'], row['longitude']), axis=1)
    df.drop(columns=['latitude', 'longitude'], inplace=True)

    df['total_capacity'] = df['occupancy'] + df['vacancy']
    df['relative_occupancy'] = df['occupancy'] / df['total_capacity']
    df['rounded_timestamp'] = df['timestamp'].dt.floor('h')

    df_aggregated = df.groupby(['parking_id', 'rounded_timestamp'], as_index=False).agg(
    mean_occupancy=('relative_occupancy', 'mean'),
    parking_type=('parking_type', 'first'),  # Directly aggregate parking_type
    zone=('zone', 'first')  # Directly aggregate zone
    )
    df_aggregated.rename(columns={'rounded_timestamp': 'timestamp'}, inplace=True)

    # Add features
    df_aggregated['hour'] = df_aggregated['timestamp'].dt.hour
    df_aggregated['day_of_week'] = df_aggregated['timestamp'].dt.dayofweek
    df_aggregated['is_festive'] = df_aggregated['timestamp'].dt.date.isin(
        pd.to_datetime(festive_dates).date
    ) | (df_aggregated['day_of_week'] == 6)

    # Encode zones
    df_aggregated['zone'] = df_aggregated['zone'].astype(str)
    parking_dummies_zone = pd.get_dummies(df_aggregated['zone'], prefix='zone')
    df_aggregated = df_aggregated.join(parking_dummies_zone).drop(columns=['zone', 'timestamp', 'parking_id'])

    # Encode parking type
    df_aggregated['parking_type'] = df_aggregated['parking_type'].astype(str)
    parking_dummies = pd.get_dummies(df_aggregated['parking_type'], prefix='parking')
    df_aggregated = df_aggregated.join(parking_dummies).drop(columns=['parking_type'])

    # Rename and prepare training data
    df_aggregated.rename(columns={'occupancy': 'mean_occupancy'}, inplace=True)
    y_train = df_aggregated['mean_occupancy']
    
    X_train = df_aggregated.drop(columns=['mean_occupancy'])
    X_train = X_train.astype(int)
    X_train = X_train.apply(pd.to_numeric, errors='coerce').fillna(X_train.mean())

    print(X_train.head())

    # Train SARIMA model
    try:
        print("Training SARIMA model...")
        sarima_model = SARIMAX(
            y_train,
            exog=X_train,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 24),
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        sarima_result = sarima_model.fit(disp=False)
        print("Model trained successfully.")
    except Exception as e:
        print(f"Error training SARIMA model: {e}", file=sys.stderr)
        return

    # Save the model
    try:
        with open("data_processor/sarima_model.pkl", "wb") as f:
            pickle.dump(sarima_result, f)
        print("Model saved successfully.")
    except Exception as e:
        print(f"Error saving model: {e}", file=sys.stderr)

def main():
    train_model()

if __name__ == "__main__":
    main()
