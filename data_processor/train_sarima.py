import pandas as pd
from datetime import datetime, timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sqlalchemy import create_engine
import pickle
import sys
import utils

def train_model(start_time=datetime.now(), end_time=None, festive_dates=None):
    """Train a SARIMA model on data from previous weeks from all entries to forecast parking occupancy."""
    if end_time is None:
        end_time = start_time - timedelta(days=14)
    elif end_time > start_time:
        raise ValueError("End time must be before start time")
    
    if festive_dates is None:
        festive_dates = utils.get_festive_dates()

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
    df['zone'] = df.apply(lambda row: utils.get_zone(row['latitude'], row['longitude']), axis=1)
    df.drop(columns=['latitude', 'longitude'], inplace=True)

    df['total_capacity'] = df['occupancy'] + df['vacancy']
    df['relative_occupancy'] = df['occupancy'] / df['total_capacity']
    df['rounded_timestamp'] = df['timestamp'].dt.floor('h')

    df_aggregated = df.groupby(['parking_id', 'rounded_timestamp'], as_index=False).agg(
    mean_occupancy=('relative_occupancy', 'mean'),
    parking_type=('parking_type', 'first'),
    zone=('zone', 'first')
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

    print("Updating parking prices...")
    utils.update_prices()
    print("Prices updated successfully.")

    print("Deleting old entries...")
    utils.delete_old_entries(30)
    print("Old entries deleted successfully.")

if __name__ == "__main__":
    main()
