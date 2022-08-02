# --- SETUP --- #

import os

import numpy as np
import pandas as pd

from cognite.client import CogniteClient
from cognite.client.data_classes import TimeSeries

from preprocess_timeseries_unknown_turbine import ts_df

# Create a function to make time series more easily
def make_timeseries(asset_name, timeseries_name, unit_name, **kwargs):
    full_name = asset_name + ":" + timeseries_name
    timeseries = TimeSeries(
        name = full_name.capitalize(),
        external_id = full_name.upper(),
        legacy_name = full_name.upper(),
        asset_id = client.assets.retrieve(external_id=asset_name.upper()).id,
        unit = unit_name.title(),
        **kwargs
    )
    return timeseries

# Specify parameters for time series to be created
args_lst = [
    # Each entry should be of the following format:
    # ([asset_external_ID, timeseries_name, unit_of_measurement], {additional_keyward_args})
    (["unknown:turbine_1:rotor", "temperature_1", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:rotor", "temperature_2", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:nacelle", "ambient_temperature_1", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:nacelle", "ambient_temperature_2", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:nacelle", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:nacelle", "cabinet_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:tower", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:controller", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:transformer", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:blade_a", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:blade_b", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:blade_c", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:blade_a", "pitch_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:blade_b", "pitch_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:blade_c", "pitch_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:stator", "temperature_1", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:stator", "temperature_2", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:spinner", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:front_bearing", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:rear_bearing", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1", "operating_hours", "hours"], {}),
    (["unknown:turbine_1", "ambient_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:anemometer", "avg_windspeed", "meter per second (m/s)"], {}),
    (["unknown:turbine_1:anemometer", "min_windspeed", "meter per second (m/s)"], {}),
    (["unknown:turbine_1:anemometer", "max_windspeed", "meter per second (m/s)"], {}),
    (["unknown:turbine_1:rotor", "avg_rotation", "revolutions per minute (rpm)"], {}),
    (["unknown:turbine_1:rotor", "min_rotation", "revolutions per minute (rpm)"], {}),
    (["unknown:turbine_1:rotor", "max_rotation", "revolutions per minute (rpm)"], {}),
    (["unknown:turbine_1:inverter", "avg_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "temperature_std", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "yaw_inv_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "fan_inv_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys1_inv1_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys1_inv2_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys1_inv3_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys1_inv4_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys1_inv5_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys1_inv6_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys1_inv7_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys2_inv1_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys2_inv2_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys2_inv3_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys2_inv4_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys2_inv5_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys2_inv6_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:inverter", "sys2_inv7_temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:generator", "production_kWh", "kilowatt-hour (kWh)"], {}),
    (["unknown:turbine_1:generator", "production_minutes", "minutes"], {}),
    (["unknown:turbine_1:generator", "avg_power", ""], {}),
    (["unknown:turbine_1:generator", "min_power", ""], {}),
    (["unknown:turbine_1:generator", "max_power", ""], {}),
    (["unknown:turbine_1:generator", "avg_reactive_power", ""], {}),
    (["unknown:turbine_1:generator", "min_reactive_power", ""], {}),
    (["unknown:turbine_1:generator", "max_reactive_power", ""], {}),
    (["unknown:turbine_1:blade_a", "avg_angle", ""], {}),
    (["unknown:turbine_1:nacelle", "avg_position", ""], {}),
    (["unknown:turbine_1", "avg_p_from_wind", ""], {}),
    (["unknown:turbine_1", "avg_p_technical_reasons", ""], {}),
    (["unknown:turbine_1", "avg_p_force_major_reasons", ""], {}),
    (["unknown:turbine_1", "avg_p_force_external_reasons", ""], {}),
    (["unknown:turbine_1:rectifier", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:main_carrier", "temperature", "degrees celsius (c)"], {}),
    (["unknown:turbine_1:remote_terminal_unit", "setpoint_1", ""], {"is_step":True})
]

# --- MAIN --- #

def main():
    # Connect to server
    client = CogniteClient(
        client_name="sangyoon.park",
        project="cec",
        api_key=os.environ.get("API_KEY_CDF_CEC")
    )

    # Check login status
    print(client.login.status())

    # Create time series in CDF
    turbine_timeseries = [make_timeseries(*args, **kwargs) for args, kwargs in args_lst]
    client.time_series.create(turbine_timeseries)

    # Replace external IDs (string) with the corresponding asset IDs (number)
    ts_df.columns = [client.time_series.retrieve(external_id=col).id for col in ts_df.columns]

    # Put the data points into CDF
    client.datapoints.insert_dataframe(ts_df)

if __name__ == "__main__":
    main()
