import os
import time
from cognite.experimental import CogniteClient
from preprocess_timeseries_unknown_turbine import rename_dict


# Get time series external IDs to be retrieved
data = {"external_ids" : list(rename_dict.values())}


# Define the function to be deployed
def handle(client, data):
    import time
    import numpy as np
    import pandas as pd
    from cognite.experimental import CogniteClient

    # Ensure to use the experimental SDK
    client = CogniteClient(
        client_name=client.config.client_name,
        project=client.config.project,
        base_url=client.config.base_url,
        api_key=client.config.api_key,
    )

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
        external_id=data["external_ids"],
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


def main():
    # Connect to server
    client = CogniteClient(
        client_name="sangyoon.park",
        project="cec",
        api_key=os.environ.get("API_KEY_CDF_CEC"),
    )

    # Check login status
    print(client.login.status())

    # Create the function in CDF
    func_name = "unknown:turbine_1:func:timeseries_livefeed"
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

    # call the function
    func_call = func.call(data=data)
    if len(func_call.get_logs()) == 0:
        print("CDF function called successfully")
    else:
        print(func_call.get_logs())

    # Schedule to run the function every 10 min
    schedule = client.functions.schedules.create(
        name=(func_name + ":" + "every10min").capitalize(),
        function_external_id=func_name.upper(),
        cron_expression = "*/10 * * * *",
        data=data,
    )
    print("CDF function scheduled for deployment")


if __name__ == "__main__":
    main()
