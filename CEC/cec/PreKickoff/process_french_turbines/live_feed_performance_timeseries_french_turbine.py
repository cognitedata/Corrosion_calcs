# --- SETUP ---#

from cognite.experimental import CogniteClient
from cognite.client.data_classes import Event, Asset, TimeSeries
import pandas as pd
from getpass import getpass
import numpy as np
from datetime import datetime
import scipy.optimize as opt
from collections import Counter

# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                  client_name = 'yutong.zhou',
                  project = 'cec')

# Check login status
print(c.login.status())

# --- PREPROCESSING --- #

df_80790 = pd.read_csv('french_turbine_D.csv')
df_80790 = df_80790.dropna(subset=['Active_power', 'Wind_speed']).copy()

# --- POWER CURVE MODELING --- #

power_fitted = dict(df_80790.groupby('Wind_speed')['Active_power'].median())
X = df_80790['Wind_speed']
y = df_80790['Active_power']

for index, row in df_80790.iterrows():
    performance = 100*(row['Active_power']+1)/(power_fitted[row['Wind_speed']]+1)
    if performance < 50:
        df_80790.loc[index, 'France:Performance_R80790'] = 50
    elif performance > 200:
        df_80790.loc[index, 'France:Performance_R80790'] = 200
    else:
        df_80790.loc[index, 'France:Performance_R80790'] = performance

df_80790['Datetime_UTC'] = pd.to_datetime(df_80790['Datetime_UTC'], format='%Y-%m-%d %H:%M:%S%z')
df_80790['Time'] = df_80790['Datetime_UTC'].astype(int)/int(1e6)
df_80790_performance = df_80790[['France:Performance_R80790']].copy()
df_80790_performance.index = df_80790['Time']

# --- FRONTFILL TIME SERIES --- #

c.time_series.create(TimeSeries(external_id="France:Performance_R80790",
                                name="France:Performance_R80790", unit="Percent (%)",
                                asset_id="7549988907359328", legacy_name="France:Performance_R80790"))

# Replace external IDs (string) with the corresponding asset IDs (number)
df_80790_performance.columns = [c.time_series.retrieve(external_id=col).id for col in df_80790_performance.columns]

# Replicate and put data points into CDF
TIME_NOW = round(time.time() * 1000) # Current UNIX time in milliseconds
while df_80790_performance.index[0] < TIME_NOW:
    try:
        ts_input = df_80790_performance[df_80790_performance.index < TIME_NOW]
        c.datapoints.insert_dataframe(ts_input)
        print(f"Timestamps from {ts_input.index[0]} to {ts_input.index[-1]} inserted")
    except Exception as e:
        print(e)
    new_datetime = pd.to_datetime(df_80790_performance.index, unit='ms', origin='unix', utc=True) + pd.offsets.DateOffset(years=6)
    df_80790_performance.index = (new_datetime.astype(int) / int(1e6)).astype(int) # Convert UTC datetime to UNIX time in ms

# --- DEPLOY FUNCTION --- #

# Get time series external IDs to be retrieved
data = {"external_ids" : 'France:Performance_R80790'}

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
func_name = "france:turbine_80790:func:performance_timeseries_livefeed"
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
