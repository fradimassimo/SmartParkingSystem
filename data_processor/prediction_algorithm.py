import processed_data_generator as pdg
import pandas as pd
from datetime import datetime, timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error

start_time = datetime(2025, 1, 30, 23, 45)
end_time = datetime(2025, 1, 2, 0, 0)
time_interval = timedelta(minutes=15)


data = pdg.generate_fake_parking_data(start_time, end_time, time_interval, [1,2,3])


df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

df['total_capacity'] = df['occupancy'] + df['vacancy']
df['relative_occupancy'] = df['occupancy'] / df['total_capacity']
# Round timestamps to the nearest hour
df['rounded_timestamp'] = df['timestamp'].dt.floor('h')

# Group by parking_id and rounded timestamp, then aggregate
df_aggregated = df.groupby(['parking_id', 'rounded_timestamp'], as_index=False).agg(
    mean_occupancy=('relative_occupancy', 'mean')  # Aggregate occupancy
)
df_aggregated.rename(columns={'rounded_timestamp': 'timestamp'}, inplace=True)

# Extract features
df_aggregated['hour'] = df_aggregated['timestamp'].dt.hour
df_aggregated['day_of_week'] = df_aggregated['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
df_aggregated['is_festive'] = df_aggregated['day_of_week'].apply(lambda x: 1 if x == 6 else 0)  # Sunday is festive

# Other festive dates
festive_dates = ["2025-01-01", "2025-01-06", "2025-04-20", "2025-04-21", "2025-05-01", "2025-04-25",
                 "2025-08-15","2025-12-08","2025-12-25","2025-12-26"]  # Add other dates here
df_aggregated['is_festive'] = df_aggregated['timestamp'].dt.date.isin(pd.to_datetime(festive_dates).date) | df_aggregated['is_festive']

# Create dummies
df_aggregated['parking_id'] = df_aggregated['parking_id'].astype(str) 
parking_dummies = pd.get_dummies(df_aggregated['parking_id'], prefix='parking')
df_aggregated = df_aggregated.join(parking_dummies).drop(columns=['parking_id', 'timestamp'])

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
