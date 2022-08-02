# --- SETUP --- #

import os
import time

import numpy as np
import pandas as pd

from cognite.client import CogniteClient
from cognite.client.data_classes import TimeSeries

from preprocess_timeseries_unknown_turbine import ts_df_augmented

# --- MAIN --- #

# Connect to server
client = CogniteClient(
    client_name="sangyoon.park",
    project="cec",
    api_key=os.environ.get("API_KEY_CDF_CEC")
)

# Check login status
print(client.login.status())

# Replace external IDs (string) with the corresponding asset IDs (number)
ts_df_augmented.columns = [client.time_series.retrieve(external_id=col).id for col in ts_df_augmented.columns]

# Replicate and put data points into CDF
TIME_NOW = round(time.time() * 1000) # Current UNIX time in milliseconds
while ts_df_augmented.index[0] < TIME_NOW:
    try:
        ts_input = ts_df_augmented[ts_df_augmented.index < TIME_NOW]
        client.datapoints.insert_dataframe(ts_input)
        print(f"Timestamps from {ts_input.index[0]} to {ts_input.index[-1]} inserted")
    except Exception as e:
        print(e)
    new_datetime = pd.to_datetime(ts_df_augmented.index, unit='ms', origin='unix', utc=True) + pd.offsets.DateOffset(years=1)
    ts_df_augmented.index = (new_datetime.astype(int) / int(1e6)).astype(int) # Convert UTC datetime to UNIX time in ms
