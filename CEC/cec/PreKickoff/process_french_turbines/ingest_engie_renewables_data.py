from getpass import getpass

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as datetime

from cognite.client import CogniteClient
from cognite.client.data_classes import Asset
from cognite.client.data_classes import TimeSeries

# Connect to server
c = CogniteClient(api_key= getpass('Enter API-Key:'), 
                  client_name = 'yanyu.zhong',
                  project = 'cec')

# Check login status
c.login.status()

# Read Data from csv file
wind_data = pd.read_csv(r"C:\Users\Lenovo\Desktop\turbineData.csv")
wind_data.head()

newCol = list(wind_data.columns)[0].split(";")
print(newCol)

# Create new pandas dataframe with the split columns
data = []
new_wind_data = pd.DataFrame(data, columns=newCol)
new_wind_data.head()

# Split all datapoints in wind_data
datapoints = []
for idx, row in wind_data.iterrows():
    datapoints.append(list(row)[0].split(";"))
dataseries = []
for row in datapoints:
    dataseries.append(pd.Series(row, index=new_wind_data.columns))
modified_wind_data = new_wind_data.append(dataseries, ignore_index=True)
modified_wind_data.head()

# Select columns with average value
newCols = list(filter(lambda string: "avg" in string, newCol))
newCols.insert(0, "Date_time")
newCols.remove('Pas_avg')
# print(newCols)
selectedDatapoints = pd.DataFrame(modified_wind_data[newCols])
selectedDatapoints.head()
# Convert string to float and ingest timeseries in CDF
for i in newCols[1:]:
    selectedDatapoints[i] = pd.to_numeric(selectedDatapoints[i])

# Convert json datetime to miliseconds
updateTime = selectedDatapoints["Date_time"]
print(updateTime)
for i in range(len(updateTime)):
    updateTime[i] = datetime.datetime.strptime(updateTime[i][:-6], '%Y-%m-%dT%H:%M:%S')
    updateTime[i] = updateTime[i].timestamp() * 1000
print(updateTime[:5])

# Replace NaN with average of the column
selectedDatapoints = selectedDatapoints.fillna(selectedDatapoints.mean())
selectedDatapoints = selectedDatapoints.dropna(axis='columns')
selectedDatapoints.head()

# Create asset hierarchy
turbine_assets = [Asset(name="vane", external_id="VANE_1", parent_external_id="TURBINE_1")]
c.assets.create_hierarchy(turbine_assets)

# Create timeseries data
timeseries = [TimeSeries(external_id="Generator_converter_speed_1", name="Generator_converter_speed", unit="rpm", asset_id="6872842694826457", legacy_name="Generator_converter_speed_1"),
              TimeSeries(external_id="Generator_bearing_1_temperature_1", name="Generator_bearing_1_temperature", unit="deg_C", asset_id="6872842694826457", legacy_name="Generator_bearing_1_temperature_1"),
              TimeSeries(external_id="Generator_bearing_2_temperature_2", name="Generator_bearing_2_temperature", unit="deg_C", asset_id="6872842694826457", legacy_name="Generator_bearing_2_temperature_2"),
              TimeSeries(external_id="Generator_speed_1", name="Generator_speed", unit="rpm", asset_id="6872842694826457", legacy_name="Generator_speed_1"),
              TimeSeries(external_id="Pitch_angle_1", name="Pitch_angle", unit="deg", asset_id="380191876472218", legacy_name="Pitch_angle_1"),
              TimeSeries(external_id="Converter_torque_1", name="Converter_torque", unit="Nm", asset_id="744379939576409", legacy_name="Converter_torque_1"),
              TimeSeries(external_id="Power_factor_1", name="Power_factor", unit="p/s", asset_id="6872842694826457", legacy_name="Power_factor_1"),
             TimeSeries(external_id="Generator_stator_temperature_1", name="Generator_stator_temperature", unit="deg_C", asset_id="6872842694826457", legacy_name="Generator_stator_temperature_1"),
              TimeSeries(external_id="Gearbox_bearing_1_temperature_1", name="Gearbox_bearing_1_temperature", unit="deg_C", asset_id="8379121053036247", legacy_name="Gearbox_bearing_1_temperature_1"),
              TimeSeries(external_id="Gearbox_bearing_2_temperature_2", name="Gearbox_bearing_2_temperature", unit="deg_C", asset_id="8379121053036247", legacy_name="Gearbox_bearing_2_temperature_2"),
              TimeSeries(external_id="Gearbox_inlet_temperature_1", name="Gearbox_inlet_temperature", unit="deg_C", asset_id="8379121053036247", legacy_name="Gearbox_inlet_temperature_1"),
              TimeSeries(external_id="Gearbox_oil_sump_temperature_1", name="Gearbox_oil_sump_temperature", unit="deg_C", asset_id="8379121053036247", legacy_name="Gearbox_oil_sump_temperature_1"),
              TimeSeries(external_id="Nacelle_angle_corrected_1", name="Nacelle_angle_corrected", unit="deg", asset_id="1043239258283514", legacy_name="Nacelle_angle_corrected_1"),
              TimeSeries(external_id="Grid_frequency_1", name="Grid_frequency", unit="Hz", asset_id="6872842694826457", legacy_name="Grid_frequency_1"),
              TimeSeries(external_id="Grid_voltage_1", name="Grid_voltage", unit="V", asset_id="6872842694826457", legacy_name="Grid_voltage_1"),
              TimeSeries(external_id="Outdoor_temperature_1", name="Outdoor_temperature", unit="deg_C", asset_id="405360689991964", legacy_name="Outdoor_temperature_1"),
              TimeSeries(external_id="Active_power_1", name="Active_power", unit="kW", asset_id="6872842694826457", legacy_name="Active_power_1"),
              TimeSeries(external_id="Pitch_angle_setpoint_1", name="Pitch_angle_setpoint", unit="N/A", asset_id="5681914295525584", legacy_name="Pitch_angle_setpoint_1"),
              TimeSeries(external_id="Reactive_power_1", name="Reactive_power", unit="kVAr", asset_id="6872842694826457", legacy_name="Reactive_power_1"),
              TimeSeries(external_id="Rotor_bearing_temperature_1", name="Rotor_bearing_temperature", unit="deg_C", asset_id="2949329976931428", legacy_name="Rotor_bearing_temperature_1"),
              TimeSeries(external_id="Torque_1", name="Torque", unit="Nm", asset_id="2949329976931428", legacy_name="Torque_1"),
              TimeSeries(external_id="Rotor_speed_1", name="Rotor_speed", unit="rpm", asset_id="2949329976931428", legacy_name="Rotor_speed_1"),
              TimeSeries(external_id="Hub_temperature_1", name="Hub_temperature", unit="deg_C", asset_id="6263146324849351", legacy_name="Hub_temperature_1"),
              TimeSeries(external_id="Apparent_power_1", name="Apparent_power", unit="kVA", asset_id="6872842694826457", legacy_name="Apparent_power_1"),
              TimeSeries(external_id="Vane_position_1", name="Vane_position", unit="deg", asset_id="3290038027036320", legacy_name="Vane_position_1"),
              TimeSeries(external_id="Vane_position_1_1", name="Vane_position_1", unit="deg", asset_id="3290038027036320", legacy_name="Vane_position_1_1"),
              TimeSeries(external_id="Vane_position_2_1", name="Vane_position_2", unit="deg", asset_id="3290038027036320", legacy_name="Vane_position_2_1"),
              TimeSeries(external_id="Absolute_wind_direction_1", name="Absolute_wind_direction", unit="deg", asset_id="3290038027036320", legacy_name="Absolute_wind_direction_1"),
              TimeSeries(external_id="Absolute_wind_direction_corrected_1", name="Absolute_wind_direction_corrected", unit="deg", asset_id="3290038027036320", legacy_name="Absolute_wind_direction_corrected_1"),
              TimeSeries(external_id="Wind_speed_2", name="Wind_speed", unit="m/s", asset_id="3290038027036320", legacy_name="Wind_speed_2"),
              TimeSeries(external_id="Wind_speed_1_1", name="Wind_speed_1", unit="m/s", asset_id="3290038027036320", legacy_name="Wind_speed_1_1"),
              TimeSeries(external_id="Wind_speed_2_1", name="Wind_speed_2", unit="m/s", asset_id="3290038027036320", legacy_name="Wind_speed_2_1"),
              TimeSeries(external_id="Nacelle_angle_1", name="Nacelle_angle", unit="deg", asset_id="1043239258283514", legacy_name="Nacelle_angle_1"),
              TimeSeries(external_id="Nacelle_temperature_2", name="Nacelle_temperature", unit="deg_C", asset_id="1043239258283514", legacy_name="Nacelle_temperature_2")
             ]
c.time_series.create(timeseries)

# Get all the ids for timeseries
ids = [c.time_series.retrieve(external_id="Pitch_angle_1").id, 
       c.time_series.retrieve(external_id="Hub_temperature_1").id,
      c.time_series.retrieve(external_id="Generator_converter_speed_1").id,
      c.time_series.retrieve(external_id="Converter_torque_1").id,
       c.time_series.retrieve(external_id="Active_power_1").id,
       c.time_series.retrieve(external_id="Reactive_power_1").id,
       c.time_series.retrieve(external_id="Apparent_power_1").id,
       c.time_series.retrieve(external_id="Power_factor_1").id,
       c.time_series.retrieve(external_id="Generator_speed_1").id,
       c.time_series.retrieve(external_id="Generator_bearing_1_temperature_1").id,
       c.time_series.retrieve(external_id="Generator_bearing_2_temperature_2").id,
       c.time_series.retrieve(external_id="Generator_stator_temperature_1").id,
       c.time_series.retrieve(external_id="Gearbox_bearing_1_temperature_1").id,
       c.time_series.retrieve(external_id="Gearbox_bearing_2_temperature_2").id,
       c.time_series.retrieve(external_id="Gearbox_inlet_temperature_1").id,
       c.time_series.retrieve(external_id="Gearbox_oil_sump_temperature_1").id,
       c.time_series.retrieve(external_id="Nacelle_angle_1").id,
       c.time_series.retrieve(external_id="Nacelle_temperature_2").id,
       c.time_series.retrieve(external_id="Wind_speed_1_1").id,
       c.time_series.retrieve(external_id="Wind_speed_2_1").id,
       c.time_series.retrieve(external_id="Wind_speed_2").id, 
       c.time_series.retrieve(external_id="Absolute_wind_direction_1").id, 
       c.time_series.retrieve(external_id="Vane_position_1_1").id, 
       c.time_series.retrieve(external_id="Vane_position_2_1").id, 
       c.time_series.retrieve(external_id="Vane_position_1").id, 
       c.time_series.retrieve(external_id="Outdoor_temperature_1").id, 
       c.time_series.retrieve(external_id="Grid_frequency_1").id, 
       c.time_series.retrieve(external_id="Grid_voltage_1").id, 
       c.time_series.retrieve(external_id="Rotor_speed_1").id, 
       c.time_series.retrieve(external_id="Rotor_bearing_temperature_1").id,
       c.time_series.retrieve(external_id="Torque_1").id,
       c.time_series.retrieve(external_id="Absolute_wind_direction_corrected_1").id,
       c.time_series.retrieve(external_id="Nacelle_angle_corrected_1").id
      ]

# Rename the column name to timeseries ids
col = {}
i = 1
j = 0
while j < len(ids):
    col[newCols[i]] = ids[j]
    i += 1
    j += 1
print(col)

selectedDatapoints = selectedDatapoints.rename(columns=col)
selectedDatapoints = selectedDatapoints.set_index('Date_time')
selectedDatapoints.head()

# Put the time series into CDF
c.datapoints.insert_dataframe(selectedDatapoints)