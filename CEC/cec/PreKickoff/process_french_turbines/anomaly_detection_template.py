# This is a template for automatic anomaly detection deployed as a Cognite Function.
# The template assume that outside libraries can be freely imported in Cognite Fucntion.
from getpass import getpass

import numpy as np
import pandas as pd
import datetime as datetime

import time
from cognite.experimental import CogniteClient

# Connect to server
c = CogniteClient(api_key=getpass('Enter API-Key:'),
                  client_name='your_client_name',
                  project='cec')

# Check login status
c.login.status()

# Root asset id for French turbine data, change to the desired root asset ids if necessary
root_asset_ids = [5772807107818762]
# Retrieve time series external ids
time_series = c.time_series(root_asset_ids=root_asset_ids, limit=None)
# Store the external_ids of the time series
external_ids = []
time_series_2_asset_id = {}
for ts in time_series:
    external_ids.append(ts.external_id)
    time_series_2_asset_id[ts.external_id] = ts.asset_id
# Create a dictionary to hold the external ids that will later be used in the hanlde function
data = {"external_ids": external_ids,
        "time_series_2_asset_id": time_series_2_asset_id}

# Define the function to be deployed


def handle(client, data):
    import time
    import numpy as np
    import pandas as pd
    from fbprophet import Prophet
    from cognite.experimental import CogniteClient
    from cognite.client.data_classes import Event

    # Ensure to use the experimental SDK
    client = CogniteClient(
        client_name=client.config.client_name,
        project=client.config.project,
        base_url=client.config.base_url,
        api_key=client.config.api_key,
    )

    ### Below functions are used for single time series ###
    # Apply training set to fit the specified model and make prediction
    # Return a pandas dataframe containing the prediction
    # This template is using Prophet library to predict 1 day ahead
    def predict(dataframe, interval_width=0.9, changepoint_range=0.8):
        m = Prophet(daily_seasonality=False, yearly_seasonality=False, weekly_seasonality=False,
                    seasonality_mode='multiplicative',
                    interval_width=interval_width,
                    changepoint_range=changepoint_range)
        m = m.fit(dataframe)
        future = m.make_future_dataframe(periods=1)
        forecast = m.predict(future)
        return forecast

    # Compare prediction with actual datapoints to find out anomalies
    # Return a pandas dataframe with all anomaly datapoints
    # This template detects anomalies for the points within an hour
    def detect_anomalies(forecast, real, external_id):
        forecasted = forecast[['ds', 'trend', 'yhat',
                               'yhat_lower', 'yhat_upper']].copy()

        forecasted['anomaly'] = 0
        forecasted.loc[real[external_id] >
                       forecasted['yhat_upper'], 'anomaly'] = 1
        forecasted.loc[real[external_id] <
                       forecasted['yhat_lower'], 'anomaly'] = 1
        # Select the anomalies in the forecast
        anomalies = forecasted[[forecasted['anomaly'] == 1]]
        return anomalies

    # Report the anomalies as events with type "Anomaly Detection" in CDF
    # Returns nothing
    def report_anomalies(anomalies, external_id, asset_id, time):
        if not anomalies.empty:
            events = []
            for idx, row in anomalies.iterrows():
                events.append(Event(external_id="Anomaly"+external_id+str(idx), start_time=time,
                                    end_time=time, type="Anomaly Detection", description="Anomaly Dected at: " + external_id))
            client.events.create(events)

    # Handler function for anomaly detection
    # Returns nothing
    def anomaly_detection(series, external_id, asset_id, time):
        dataframe = series.to_frame(name=external_id)
        forecast = predict(dataframe)
        anomalies = detect_anomalies(forecast, dataframe, external_id)
        report_anomalies(anomalies, external_id, asset_id, time)
    ### Above functions are used for single time series anomaly detection ###

    # Define constants to be used
    MONTH = 30 * 24 * 60 * 60 * 1000  # Approximation of a month in milliseconds
    # One day in milliseconds (to be used for data retrieval)
    ONE_DAY = 24 * 60 * 60 * 1000

    # Get the current UNIX time in milliseconds
    time_now = int(time.time() * 1000)

    # Retrieve data points from a month ago for prediction, return a pandas dataframe
    ts_df = c.datapoints.retrieve_dataframe(
        external_id=external_ids,
        start=(time_now - MONTH - ONE_DAY),
        end=(time_now - ONE_DAY),
        aggregates=["average"],
        granularity='10m'
    )

    # Apply the anomaly detection functions to each time series
    # series.name[:-8] is to remove the "|average" in the column names of the retrieved datapoint dataframe
    ts_df.apply(lambda series: anomaly_detection(series, series.name,
                                                 data["time_series_2_asset_id"][series.name[:-8]], time_now))

    return True


# Create the function in CDF
# Change this to desired func_name
func_name = "french_turbines:func:timeseries_anomaly_detection"
func = c.functions.create(
    name=func_name.capitalize(),
    external_id=func_name.upper(),
    function_handle=handle,
    api_key=getpass("API-KEY: "),
)
print("CDF function created")

# Setup schedule
schedule = c.functions.schedules.create(
    name=(func_name + ":" + "everyday").capitalize(),
    function_external_id=func_name.upper(),
    cron_expression="0 0 12 * * ?",  # Fire at 12pm everyday
    data=data
)
print("successfully set up the schedule")
