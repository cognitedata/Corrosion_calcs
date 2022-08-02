# The data was obtained on 06/24/2020 from:
# https://www.kaggle.com/wasuratme96/iiot-data-of-wind-turbine

# --- SETUP --- #

import os
from collections import Counter

import numpy as np
import pandas as pd

# Map the original column name to its target time series external ID in CDF
rename_dict = {
    "Rotor temp. 1" : "unknown:turbine_1:rotor:temperature_1",
    "Rotor temp. 2" : "unknown:turbine_1:rotor:temperature_2",
    "Nacelle ambient temp. 1" : "unknown:turbine_1:nacelle:ambient_temperature_1",
    "Nacelle ambient temp. 2" : "unknown:turbine_1:nacelle:ambient_temperature_2",
    "Nacelle temp." : "unknown:turbine_1:nacelle:temperature",
    "Nacelle cabinet temp." : "unknown:turbine_1:nacelle:cabinet_temperature",
    "Tower temp." : "unknown:turbine_1:tower:temperature",
    "Control cabinet temp." : "unknown:turbine_1:controller:temperature",
    "Transformer temp." : "unknown:turbine_1:transformer:temperature",
    "Blade A temp." : "unknown:turbine_1:blade_a:temperature",
    "Blade B temp." : "unknown:turbine_1:blade_b:temperature",
    "Blade C temp." : "unknown:turbine_1:blade_c:temperature",
    "Pitch cabinet blade A temp." : "unknown:turbine_1:blade_a:pitch_temperature",
    "Pitch cabinet blade B temp." : "unknown:turbine_1:blade_b:pitch_temperature",
    "Pitch cabinet blade C temp." : "unknown:turbine_1:blade_c:pitch_temperature",
    "Stator temp. 1" : "unknown:turbine_1:stator:temperature_1",
    "Stator temp. 2" : "unknown:turbine_1:stator:temperature_2",
    "Spinner temp." : "unknown:turbine_1:spinner:temperature",
    "Front bearing temp." : "unknown:turbine_1:front_bearing:temperature",
    "Rear bearing temp." : "unknown:turbine_1:rear_bearing:temperature",
    "WEC: Operating Hours" : "unknown:turbine_1:operating_hours",
    "Ambient temp." : "unknown:turbine_1:ambient_temperature",
    "WEC: ava. windspeed" : "unknown:turbine_1:anemometer:avg_windspeed",
    "WEC: min. windspeed" : "unknown:turbine_1:anemometer:min_windspeed",
    "WEC: max. windspeed" : "unknown:turbine_1:anemometer:max_windspeed",
    "WEC: ava. Rotation" : "unknown:turbine_1:rotor:avg_rotation",
    "WEC: min. Rotation" : "unknown:turbine_1:rotor:min_rotation",
    "WEC: max. Rotation" : "unknown:turbine_1:rotor:max_rotation",
    "Inverter averages" : "unknown:turbine_1:inverter:avg_temperature",
    "Inverter std dev" : "unknown:turbine_1:inverter:temperature_std",
    "Yaw inverter cabinet temp." : "unknown:turbine_1:inverter:yaw_inv_temperature",
    "Fan inverter cabinet temp." : "unknown:turbine_1:inverter:fan_inv_temperature",
    "Sys 1 inverter 1 cabinet temp." : "unknown:turbine_1:inverter:sys1_inv1_temperature",
    "Sys 1 inverter 2 cabinet temp." : "unknown:turbine_1:inverter:sys1_inv2_temperature",
    "Sys 1 inverter 3 cabinet temp." : "unknown:turbine_1:inverter:sys1_inv3_temperature",
    "Sys 1 inverter 4 cabinet temp." : "unknown:turbine_1:inverter:sys1_inv4_temperature",
    "Sys 1 inverter 5 cabinet temp." : "unknown:turbine_1:inverter:sys1_inv5_temperature",
    "Sys 1 inverter 6 cabinet temp." : "unknown:turbine_1:inverter:sys1_inv6_temperature",
    "Sys 1 inverter 7 cabinet temp." : "unknown:turbine_1:inverter:sys1_inv7_temperature",
    "Sys 2 inverter 1 cabinet temp." : "unknown:turbine_1:inverter:sys2_inv1_temperature",
    "Sys 2 inverter 2 cabinet temp." : "unknown:turbine_1:inverter:sys2_inv2_temperature",
    "Sys 2 inverter 3 cabinet temp." : "unknown:turbine_1:inverter:sys2_inv3_temperature",
    "Sys 2 inverter 4 cabinet temp." : "unknown:turbine_1:inverter:sys2_inv4_temperature",
    "Sys 2 inverter 5 cabinet temp." : "unknown:turbine_1:inverter:sys2_inv5_temperature",
    "Sys 2 inverter 6 cabinet temp." : "unknown:turbine_1:inverter:sys2_inv6_temperature",
    "Sys 2 inverter 7 cabinet temp." : "unknown:turbine_1:inverter:sys2_inv7_temperature",
    "WEC: Production kWh" : "unknown:turbine_1:generator:production_kWh",
    "WEC: Production minutes" : "unknown:turbine_1:generator:production_minutes",
    "WEC: ava. Power" : "unknown:turbine_1:generator:avg_power",
    "WEC: min. Power" : "unknown:turbine_1:generator:min_power",
    "WEC: max. Power" : "unknown:turbine_1:generator:max_power",
    "WEC: ava. reactive Power" : "unknown:turbine_1:generator:avg_reactive_power",
    "WEC: min. reactive Power" : "unknown:turbine_1:generator:min_reactive_power",
    "WEC: max. reactive Power" : "unknown:turbine_1:generator:max_reactive_power",
    "WEC: ava. blade angle A" : "unknown:turbine_1:blade_a:avg_angle",
    "WEC: ava. Nacel position including cable twisting" : "unknown:turbine_1:nacelle:avg_position",
    "WEC: ava. available P from wind" : "unknown:turbine_1:avg_p_from_wind",
    "WEC: ava. available P technical reasons" : "unknown:turbine_1:avg_p_technical_reasons",
    "WEC: ava. Available P force majeure reasons" : "unknown:turbine_1:avg_p_force_major_reasons",
    "WEC: ava. Available P force external reasons" : "unknown:turbine_1:avg_p_force_external_reasons",
    "Rectifier cabinet temp." : "unknown:turbine_1:rectifier:temperature",
    "Main carrier temp." : "unknown:turbine_1:main_carrier:temperature",
    "RTU: ava. Setpoint 1" : "unknown:turbine_1:remote_terminal_unit:setpoint_1"
}
rename_dict = {k : v.upper() for k, v in rename_dict.items()}

# --- MAIN --- #

# Read in data
scada_df = pd.read_csv('./data/scada_data.csv')

# Create a DataFrame containing data points to be ingested
ts_df = (scada_df.copy()
    .assign(time_ms = lambda x: x.Time * 1000) # Time in milliseconds
    .set_index("time_ms")
    .rename(columns=rename_dict)
    [rename_dict.values()]
)

# Identify the most frequent time interval in SCADA data
counter = Counter(ts_df.index[1:] - ts_df.index[:-1])
INTERVAL = counter.most_common(1)[0][0]

# Identify timestamps necessary for covering the full year
datetime_nextyear = pd.to_datetime(ts_df.index, unit="ms", origin="unix", utc=True) + pd.offsets.DateOffset(years=1)
timestamp_nextyear = (datetime_nextyear.astype(int)/1e6).astype(int)
timestamp_interpolate = np.arange(ts_df.index[-1] + INTERVAL, timestamp_nextyear[0], INTERVAL)

# Interpolate using values from the middle of the original data
INDEX_HALFWAY = int(ts_df.shape[0] / 2)
ts_df_interpolate = (ts_df
    .iloc[INDEX_HALFWAY:(INDEX_HALFWAY + len(timestamp_interpolate))]
    .copy()
    .set_index(timestamp_interpolate)
)
ts_df_augmented = pd.concat([ts_df, ts_df_interpolate])
