from datetime import datetime, timedelta
import pandas as pd
import pickle

def get_prediction_for_week(parking_id, start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S"), festive_dates = None, zone = None):
    """returns forecast for the next week given a parking_id and start_time. """ 
    try:
        with open("app/data_processor/sarima_model.pkl", "rb") as f:
            loaded_model = pickle.load(f)
    except Exception as e:
        print(f"Error loading model, be sure to train it first: {e}")

    new_records = []
    for i in range(168):
        new_records.append({
            "parking_id": parking_id,
            "timestamp": start_time + timedelta(hours=i)
        })

    if festive_dates is None:
        festive_dates = get_festive_dates()

    df_aggregated = pd.DataFrame(new_records)
    df_aggregated['timestamp'] = pd.to_datetime(df_aggregated['timestamp'])

    df_aggregated['hour'] = df_aggregated['timestamp'].dt.hour
    df_aggregated['day_of_week'] = df_aggregated['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    df_aggregated['is_festive'] = df_aggregated['day_of_week'].apply(lambda x: 1 if x == 6 else 0)  # Sunday is festive
    df_aggregated['is_festive'] = df_aggregated['timestamp'].dt.date.isin(pd.to_datetime(festive_dates).date) | df_aggregated['is_festive']

    # Create dummies
    df_aggregated['parking_id'] = df_aggregated['parking_id'].astype(str) 
    parking_dummies = pd.get_dummies(df_aggregated['parking_id'], prefix='parking')
    df_aggregated = df_aggregated.join(parking_dummies).drop(columns=['parking_id', 'timestamp'])
    
    if zone is not None:
        df_aggregated['zone'] = zone
        zone_dummies = pd.get_dummies(df_aggregated['zone'], prefix='zone')
        df_aggregated = df_aggregated.join(zone_dummies).drop(columns=['zone'])
    
    df_aggregated = df_aggregated.astype(int)
    df_aggregated = df_aggregated.apply(pd.to_numeric, errors='coerce').fillna(df_aggregated.mean())

    forecast = loaded_model.forecast(steps=168, exog=df_aggregated)

    forecast_df = pd.DataFrame({
    "parking_id": parking_id,
    "timestamp": pd.date_range(start=start_time, periods=168, freq="h"),
    "forecasted_occupancy": forecast
    })

    return forecast_df # pandas dataframe with forecasted occupancy for the next week


def get_festive_dates():
    return ["2025-01-01", "2025-01-06", "2025-04-20", "2025-04-21", "2025-05-01", "2025-04-25",
                    "2025-08-15","2025-12-08","2025-12-25","2025-12-26"]

def main():
    parking_id = "4"
    ma = get_prediction_for_week(parking_id)
    print(ma.head())
    print(ma.tail())


if __name__ == "__main__":
    main()