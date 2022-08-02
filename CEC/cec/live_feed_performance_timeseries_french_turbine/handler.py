# --- SETUP ---#

from cognite.experimental import CogniteClient
from cognite.client.data_classes import Event, Asset, TimeSeries
import pandas as pd
from getpass import getpass
import numpy as np
from datetime import datetime

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
