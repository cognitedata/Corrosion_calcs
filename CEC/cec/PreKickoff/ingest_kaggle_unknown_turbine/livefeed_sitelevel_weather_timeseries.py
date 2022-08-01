
# --- SETUP --- #

import os, sys
import time
from cognite.experimental import CogniteClient
sys.path.append("/Users/sangyoonpark/Project/Cognite/NextWind/cec") # Path to package root
from PreKickoff.utils.stormglass import stormglass_vars, handle

# Define data to be put into the handle function
data = {
    "endpoint" : "https://api.stormglass.io/v2/weather/point",
    "apikey" : os.environ.get("API_KEY_STORMGLASS"),
    "site" : "unknown",
    # Use coordinates for Humboldt Bay, CA
    "lat" : 40.811957,
    "lng" : -124.316830,
    "vars" : [
        "airTemperature",
        "pressure",
        "currentDirection",
        "currentSpeed",
        "gust",
        "humidity",
        "iceCover",
        "precipitation",
        "swellDirection",
        "swellHeight",
        "swellPeriod",
        "secondarySwellDirection",
        "secondarySwellHeight",
        "secondarySwellPeriod",
        "visibility",
        "waveDirection",
        "waveHeight",
        "wavePeriod",
        "windWaveDirection",
        "windWaveHeight",
        "windWavePeriod",
        "windDirection",
        "windDirection40m",
        "windDirection80m",
        "windSpeed",
        "windSpeed40m",
        "windSpeed80m",
    ],
}

# Connect to server
client = CogniteClient(
    client_name="sangyoon.park",
    project="cec",
    api_key=os.environ.get("API_KEY_CDF_CEC"),
)

# Check login status
print(client.login.status())

# --- CREATE TIME SERIES --- #

# Identify existing time series
existing_ts = client.time_series.list(limit=None)
existing_ts_external_id = [ts.external_id for ts in existing_ts]

# Create new time series
asset_name = data["site"]
asset_id = client.assets.retrieve(external_id=asset_name.upper()).id
new_ts = []
for varname in data["vars"]:
    full_name = asset_name + ":" + varname
    ts = TimeSeries(
        name = full_name.capitalize(),
        external_id = full_name.upper(),
        asset_id = asset_id,
        unit = stormglass_vars.get(varname, {}).get("unit"),
        description = stormglass_vars.get(varname, {}).get("description"),
    )
    if not ts.external_id in existing_ts_external_id:
        new_ts.append(ts)

# Put new time series into CDF
client.time_series.create(ts_to_create)

# --- DEPLOY CDF FUNCTION --- #

# Create the function in CDF
func_name = "unknown:func:weatherforecast_livefeed"
func = client.functions.create(
    name=func_name.capitalize(),
    external_id=func_name.upper(),
    function_handle=handle,
    api_key=client.config.api_key,
)
print("CDF function created")

# Wait until the function status changes to "ready"
while func.status != "Ready":
    func = client.functions.retrieve(external_id=func_name.upper())
    time.sleep(1)
print("CDF function ready")

# Call the function
func_call = func.call(data=data)
print(func_call.get_logs())

# Schedule to run the function every 1 hour
schedule = client.functions.schedules.create(
    name=(func_name + ":" + "every1hr").capitalize(),
    function_external_id=func_name.upper(),
    cron_expression = "0 * * * *",
    data=data,
)
print("CDF function scheduled for deployment")
