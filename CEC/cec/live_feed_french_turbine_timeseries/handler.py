# We need to use cognite's experimental sdk, so be sure to install it
# pip install cognite-sdk-experimental

from getpass import getpass
import numpy as np
import pandas as pd
import time
from cognite.experimental import CogniteClient

# Get all the time series
frenchData = c.time_series.list(root_asset_ids=[5772807107818762], limit=None)
# Store the external_ids of the time series
external_ids = []
for ts in frenchData:
    external_ids.append(ts.external_id)
# Create a dictionary to hold the external ids that will later be used in the hanlde function
data = {"external_ids": external_ids}

# Define the function to be deployed


def handle(client, data):
    import time
    import numpy as np
    import pandas as pd
    # from cognite.experimental import CogniteClient
    # from cognite.client import CogniteClient


    # Define constants to be used
    INTERVAL = 640000  # Most frequent time interval in the considered data
    YEAR = 365 * 24 * 60 * 60 * 1000  # Approximation of a year in milliseconds
    # Five days in milliseconds (to be used for data retrieval)
    FIVE_DAYS = 5 * 24 * 60 * 60 * 1000

    # Get the current UNIX time in milliseconds
    time_now = int(time.time() * 1000)

    # Retrieve data points from a year ago
    ts_lst = client.datapoints.retrieve(
        external_id=data["external_ids"],
        start=(time_now - YEAR - FIVE_DAYS),
        end=(time_now - YEAR + FIVE_DAYS)
    )

    # Transform retrieved data into DataFrame
    ts_df = ts_lst.to_pandas()
    # ts_df.index = ts_lst[0].timestamp
    # ts_df = pd.DataFrame(
    #     {ts.id: ts.value for ts in ts_lst},
    #     index=ts_lst[0].timestamp
    # )

    # Shift the year forward
    datetime_thisyear = pd.to_datetime(
        ts_df.index, unit="ms", origin="unix", utc=True) + pd.offsets.DateOffset(years=1)
    ts_df.index = (datetime_thisyear.astype(int)/1e6).astype(int)

    # Insert the most recent datapoint(s)
    ts_input = ts_df[((time_now - 2 * INTERVAL) < ts_df.index)
                     & (ts_df.index <= time_now)]
    ts_input = ts_input.dropna(axis=1)
    client.datapoints.insert_dataframe(ts_input, external_id_headers=True)

    return True

