# The data was obtained on 06/24/2020 from:
# https://www.kaggle.com/wasuratme96/iiot-data-of-wind-turbine

# --- SET UP --- #

from cognite.client import CogniteClient
from getpass import getpass
from cognite.client.data_classes import Asset, TimeSeries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                  client_name = 'yutong.zhou',
                  project = 'cec')

# Check login status
print(c.login.status())

# --- CREATE ASSET HIERARCHY --- #

# Create assets
turkey_assets = [Asset(external_id="TURKEY", name="Turkey", data_set_id=5806724017774745), 
                  Asset(external_id="TURKEY:TURBINE_1", parent_external_id="TURKEY", name="Turkey:turbine_1", data_set_id=5806724017774745)]
c.assets.create_hierarchy(turkey_assets)

# Read data
turkey_df = pd.read_csv('./data/T1.csv')

# Convert time string to milliseconds
turkey_df['Time'] =  pd.to_datetime(turkey_df['Date/Time'], format='%d %m %Y %H:%M').astype(np.int64)/int(1e6)

# --- INGEST TIME SERIES DATA --- #

# Create timeseries for wind speed
c.time_series.create(TimeSeries(external_id="TURKEY:WIND_SPEED_1", 
                                name="Turkey:wind speed 1", 
                                unit="m/s", 
                                data_set_id=5806724017774745,
                                asset_id=5811023843526776,
                                legacy_name="TURKEY:WIND_SPEED_1"))
                     
# Create timeseries for wind direction
c.time_series.create(TimeSeries(external_id="TURKEY:WIND_DIRECTION_1", 
                                name="Turkey:wind direction 1", 
                                unit="deg", 
                                data_set_id=5806724017774745,
                                asset_id=5811023843526776,
                                legacy_name="TURKEY:WIND_DIRECTION_1"))

# Create timeseries for active power
c.time_series.create(TimeSeries(external_id="TURKEY:LV_ACTIVE_POWER_1", 
                                name="Turkey:LV active power 1", 
                                unit="kW", 
                                data_set_id=5806724017774745,
                                asset_id=5811023843526776,
                                legacy_name="TURKEY:LV_ACTIVE_POWER_1"))
                     
# Create timeseries for theoretical power curve
c.time_series.create(TimeSeries(external_id="TURKEY:THEORETICAL_POWER_CURVE_1", 
                                name="Turkey:theoretical power curve 1", 
                                unit="KWh", 
                                data_set_id=5806724017774745,
                                asset_id=5811023843526776,
                                legacy_name="TURKEY:THEORETICAL_POWER_CURVE_1"))

# Prepare datapoints for ingestion
wind_speed = list(zip(turkey_df['Time'], turkey_df['Wind Speed (m/s)']))
wind_direction = list(zip(turkey_df['Time'], turkey_df['Wind Direction (°)']))                     
lv_active_power = list(zip(turkey_df['Time'], turkey_df['LV ActivePower (kW)']))
theoretical_power_curve = list(zip(turkey_df['Time'], turkey_df['Theoretical_Power_Curve (KWh)']))

# Ingest datapoints
datapoints = []
datapoints.append({"externalId": "TURKEY:WIND_SPEED_1", "datapoints": wind_speed})
datapoints.append({"externalId": "TURKEY:WIND_DIRECTION_1", "datapoints": wind_direction})
datapoints.append({"externalId": "TURKEY:LV_ACTIVE_POWER_1", "datapoints": lv_active_power})
datapoints.append({"externalId": "TURKEY:THEORETICAL_POWER_CURVE_1", "datapoints": theoretical_power_curve})
c.datapoints.insert_multiple(datapoints)