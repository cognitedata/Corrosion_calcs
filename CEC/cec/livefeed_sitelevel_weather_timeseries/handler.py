# This script uses the weather ingestion template in cec/PreKickoff/utils/stormglass.py
# with slight modification to update four turbines at the same time
from getpass import getpass

import numpy as np
import pandas as pd
import time

from cognite.experimental import CogniteClient


# --- CREATE TIME SERIES FOR FRENCH TURBINE --- #

# Store the four turbine names
turbine_names = ["_R80721", "_R80736", "_R80790", "_R80711"]

# Define data to be put into the handle function
data = {
    "endpoint": "https://api.stormglass.io/v2/weather/point",
    "apikey": getpass("API_KEY_STORMGLASS"),
    "site": ["FRANCE:TURBINE", "France:"],
    "turbine_numbers": turbine_names,
    # Use coordinates for offshore coast in French
    "lat": 46.132708,
    "lng": -1.646468,
    "vars": [
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

# --- HANDLER FOR CDF FUNCTION --- #


def handle(client, data):
    """Extract weather forecast data from Storm Glass and ingest it into a CDF tenant.
    Args:
        client (CogniteClient): A CogniteClient object logged into CEC tenant
        data (Dict): A metadata construct containing the following fields:
            endpoint (str): API endpoint (e.g., "https://api.stormglass.io/v2/weather/point")
            apikey (str): API key
            site (str): Name of the target site to which the data is to be ingested (e.g., "unknown")
            lat (float): Latitude of the target location (e.g., 40.811957)
            lng (float): Longitude of the target location (e.g., -124.316830)
            vars (List[str]): List of weather variables to be extracted (e.g., ["windSpeed", "windDirection])
    Returns:
        bool: True if the function successfully runs; False otherwise
    """
    import time
    import requests
    import numpy as np
    import pandas as pd

    # Ensure the input is valid: client
    status = client.login.status()
    if not status.logged_in:
        print("Client not logged in")
        return False

    # Ensure the input is valid: data
    input_fields = data.keys()
    expected_fields = ["endpoint", "apikey", "site", "lat", "lng", "vars"]
    missing_fields = []
    for field in expected_fields:
        if not field in input_fields:
            missing_fields.append(field)
        if len(missing_fields) > 0:
            print(
                f"The following fields are missing in the input data: {', '.join(missing_fields)}")
            return False

    # Get the list of variables to extract
    vars_to_extract = data["vars"]

    # Define time variables to use
    time_now = int(time.time())  # UNIX time in seconds
    DAY_IN_SEC = 60 * 60 * 24

    # Make an API request to get desired weather data
    response = requests.get(
        data["endpoint"],
        params={
            'lat': data["lat"],
            'lng': data["lng"],
            'params': ','.join(vars_to_extract),
            'start': time_now - DAY_IN_SEC,
            'end': time_now + 3 * DAY_IN_SEC,
        },
        headers={
            'Authorization': data["apikey"],
        }
    )

    # Skip the rest of the process if bad response
    if response.status_code != 200:
        print(f"Unexpected HTTP response status: {response.status_code}")
        return False
    print("HTTP response status is OK")

    # Extract data
    json_data = response.json()

    # Pre-allocate memory for storing extracted values as a DataFrame
    n_ts = len(json_data['hours'])
    n_vars = len(vars_to_extract)

    # Do this for all the four turbines
    for turbine_name in data['turbine_numbers']:
        ts_df = pd.DataFrame(np.zeros((n_ts, n_vars)))
        ts_df.columns = vars_to_extract
        ts_df['time'] = np.zeros(n_ts)

        # Insert extracted values into the pre-created empty DataFrame
        for i, entry in enumerate(json_data['hours']):
            ts_df.loc[i, 'time'] = entry.get('time')
            for varname in vars_to_extract:
                ts_df.loc[i, varname] = entry.get(varname, {}).get(
                    'sg')  # Use Storm Glass as source

        # Transform time into UNIX epoch time in milliseconds
        ts_df['time'] = pd.to_datetime(ts_df['time'], utc=True)
        ts_df['time'] = (ts_df['time'].astype(int)/1e6).astype(int)

        # Format DataFrame to be correctly handled by Python SDK
        ts_df.set_index('time', inplace=True)
        ts_df.columns = [data['site'][1] + colname +
                         turbine_name for colname in ts_df.columns]
        ts_df.columns = [client.time_series.retrieve(
            external_id=colname).id for colname in ts_df.columns]

        # Put the data points into CDF
        MAX_TRY = 3
        n_try = 0
        while n_try < MAX_TRY:
            try:
                client.datapoints.insert_dataframe(ts_df)
                print("Data has been inserted successfully")
                break
            except:
                n_try += 1
                print(f"Insertion failed: {n_try} times")
                time.sleep(3)
        if n_try == MAX_TRY:
            print("Data has NOT been inserted")
            return False

    return True

