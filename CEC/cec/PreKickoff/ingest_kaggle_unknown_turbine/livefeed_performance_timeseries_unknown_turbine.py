# --- SETUP --- #

from cognite.experimental import CogniteClient
from cognite.client.data_classes import Event, Asset, TimeSeries
import pandas as pd
from getpass import getpass
import numpy as np
from datetime import datetime
import scipy.optimize as opt
from collections import Counter
from preprocess_timeseries_unknown_turbine import ts_df_augmented
from ingest_timeseries_unknown_turbine import make_timeseries

# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                  client_name = 'yutong.zhou',
                  project = 'cec')

# Check login status
print(c.login.status())

# --- PREPROCESSING --- #

# Exclude outliers before modeling
df_filtered = ts_df_augmented[(ts_df_augmented['UNKNOWN:TURBINE_1:GENERATOR:AVG_POWER'] != 0) & (ts_df_augmented['UNKNOWN:TURBINE_1:ANEMOMETER:AVG_WINDSPEED'] < 22)]
df_power = df_filtered[['UNKNOWN:TURBINE_1:GENERATOR:AVG_POWER', 'UNKNOWN:TURBINE_1:ANEMOMETER:AVG_WINDSPEED']].copy()
power_avg = dict(df_power.groupby('UNKNOWN:TURBINE_1:ANEMOMETER:AVG_WINDSPEED')['UNKNOWN:TURBINE_1:GENERATOR:AVG_POWER'].mean())
power_std = dict(df_power.groupby('UNKNOWN:TURBINE_1:ANEMOMETER:AVG_WINDSPEED')['UNKNOWN:TURBINE_1:GENERATOR:AVG_POWER'].std())

large_std = {}
for key, value in power_std.items():
    if value >= 100:
        large_std[key] = value

for index, row in df_power.iterrows():
    wind_speed = row['UNKNOWN:TURBINE_1:ANEMOMETER:AVG_WINDSPEED']
    if wind_speed in large_std.keys():
        lower = power_avg[wind_speed] - 2*power_std[wind_speed]
        upper = power_avg[wind_speed] + 2*power_std[wind_speed]
        power = row['UNKNOWN:TURBINE_1:GENERATOR:AVG_POWER']
        if power < lower or power > upper:
            df_power.loc[index, 'UNKNOWN:TURBINE_1:GENERATOR:AVG_POWER'] = 0

df_clean = df_power[df_power['UNKNOWN:TURBINE_1:GENERATOR:AVG_POWER'] != 0].copy()

# --- POWER CURVE MODELING --- #

# Power curve modeling using a five parameter logistic function
X = df_clean['UNKNOWN:TURBINE_1:ANEMOMETER:AVG_WINDSPEED'].to_numpy()
y = df_clean['UNKNOWN:TURBINE_1:GENERATOR:AVG_POWER'].to_numpy()

def f(x, a, b, c, d, g):
    return d + (a-d)/(1+(x/c)**b)**g

(a_, b_, c_, d_, g_), _ = opt.curve_fit(f, X, y, p0=[3000, -10, 10, 5, 1])

X_star = ts_df_augmented['UNKNOWN:TURBINE_1:ANEMOMETER:AVG_WINDSPEED'].unique().reshape(-1, 1)
y_pred = f(X_star, a_, b_, c_, d_, g_)
power_fitted = dict(zip(ts_df_augmented['UNKNOWN:TURBINE_1:ANEMOMETER:AVG_WINDSPEED'].unique(), y_pred))

# Compute relative performance
for index, row in ts_df_augmented.iterrows():
    performance = 100*(row['UNKNOWN:TURBINE_1:GENERATOR:AVG_POWER'])/(power_fitted[row['UNKNOWN:TURBINE_1:ANEMOMETER:AVG_WINDSPEED']])
    if performance < 50:
        ts_df_augmented.loc[index, 'UNKNOWN:TURBINE_1:PERFORMANCE'] = 50
    elif performance > 200:
        ts_df_augmented.loc[index, 'UNKNOWN:TURBINE_1:PERFORMANCE'] = 200
    else:
        ts_df_augmented.loc[index, 'UNKNOWN:TURBINE_1:PERFORMANCE'] = performance

# --- FRONTFILL TIME SERIES --- #

args_lst = [
    # Each entry should be of the following format:
    # ([asset_external_ID, timeseries_name, unit_of_measurement], {additional_keyward_args})
    (["unknown:turbine_1", "performance", "percent (%)"], {})]

# Create time series in CDF
turbine_timeseries = [make_timeseries(*args, **kwargs) for args, kwargs in args_lst]
c.time_series.create(turbine_timeseries)

# Replace external IDs (string) with the corresponding asset IDs (number)
ts_performance_augmented.columns = [c.time_series.retrieve(external_id=col).id for col in ts_performance_augmented.columns]

# Replicate and put data points into CDF
TIME_NOW = round(time.time() * 1000) # Current UNIX time in milliseconds
while ts_performance_augmented.index[0] < TIME_NOW:
    try:
        ts_input = ts_performance_augmented[ts_performance_augmented.index < TIME_NOW]
        c.datapoints.insert_dataframe(ts_input)
        print(f"Timestamps from {ts_input.index[0]} to {ts_input.index[-1]} inserted")
    except Exception as e:
        print(e)
    new_datetime = pd.to_datetime(ts_performance_augmented.index, unit='ms', origin='unix', utc=True) + pd.offsets.DateOffset(years=1)
    ts_performance_augmented.index = (new_datetime.astype(int) / int(1e6)).astype(int) # Convert UTC datetime to UNIX time in ms

# --- DEPLOY FUNCTION --- #

# Get time series external IDs to be retrieved
data = {"external_ids" : 'UNKNOWN:TURBINE_1:PERFORMANCE'}

# Define the function to be deployed
def handle(client, data):
    import time
    import numpy as np
    import pandas as pd

    # Define constants to be used
    INTERVAL = 640000 # Most frequent time interval in the considered data
    YEAR = 365 * 24 * 60 * 60 * 1000 # Approximation of a year in milliseconds
    FIVE_DAYS = 5 * 24 * 60 * 60 * 1000 # Five days in milliseconds (to be used for data retrieval)

    # Get time series external IDs to be retrieved
    external_id_lst = data["external_ids"]

    # Get the current UNIX time in milliseconds
    time_now = int(time.time() * 1000)

    # Retrieve data points from a year ago
    ts_lst = client.datapoints.retrieve(
        external_id=[data["external_ids"]],
        start=(time_now - YEAR - FIVE_DAYS),
        end=(time_now - YEAR + FIVE_DAYS)
    )

    # Transform retrieved data into DataFrame
    ts_df = pd.DataFrame(
        {ts.id : ts.value for ts in ts_lst},
        index=ts_lst[0].timestamp
    )

    # Shift the year forward
    datetime_thisyear = pd.to_datetime(ts_df.index, unit="ms", origin="unix", utc=True) + pd.offsets.DateOffset(years=1)
    ts_df.index = (datetime_thisyear.astype(int)/1e6).astype(int)

    # Insert the most recent datapoint(s)
    ts_input = ts_df[((time_now - 2 * INTERVAL) < ts_df.index) & (ts_df.index <= time_now)]
    client.datapoints.insert_dataframe(ts_input)

    return True

# Create the function in CDF
func_name = "unknown:turbine_1:func:performance_timeseries_livefeed"
func = c.functions.create(
    name=func_name.capitalize(),
    external_id=func_name.upper(),
    function_handle=handle,
    api_key=api_key,
)
print("CDF function created")

# Wait until the function status changes to "ready"
while func.status != "Ready":
    func = c.functions.retrieve(external_id=func_name.upper())
    time.sleep(1)
print("CDF function ready")

# call the function
func_call = func.call(data=data)
if len(func_call.get_logs()) == 0:
    print("CDF function called successfully")
else:
    print(func_call.get_logs())

# Schedule to run the function every 10 min
schedule = c.functions.schedules.create(
    name=(func_name + ":" + "every10min").capitalize(),
    function_external_id=func_name.upper(),
    cron_expression = "*/10 * * * *",
    data=data,
)
print("CDF function scheduled for deployment")
