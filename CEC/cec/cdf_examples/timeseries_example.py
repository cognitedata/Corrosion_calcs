#import packages
from cognite.client import CogniteClient
from cognite.client.data_classes import TimeSeries, Sequence
import pandas as pd
from getpass import getpass
import datetime

# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                  client_name = 'tejo.de.groot',
                  project = 'cec')
#create variables
external_id = 'HUMBOLDT_BAY'
data_set_id = 7751435616395347
#retrieve asset
asset = c.assets.retrieve(external_id=external_id)
#retrieve all timeseries
ts = c.time_series.list(asset_external_ids=[external_id], 
                        limit=None).to_pandas()
#retrieve all timeseries datapoints in dataframe
df = c.datapoints.retrieve(external_id=ts.externalId.tolist(), 
                                     start=0, 
                                     end="now", 
                                     limit=None).to_pandas()
####Create timeseries
ts = c.time_series.create(TimeSeries(name="HUMBOLDT_BAY:FORECAST-WINDSPEED80M",
                                          external_id="HUMBOLDT_BAY:FORECAST-WINDSPEED80M",
                                          asset_id=6352781722863707,
                                          data_set_id=data_set_id))
#upload datapoints
#can insert more than one timeseries at a time. 
#Just need to make sure that the column names are set to the external_id of
#the external_id that the datapoints are being inserted for.
ts_df = pd.DataFrame([(datetime.datetime.now(), 10)], columns=['Time', 'HUMBOLDT_BAY:FORECAST-WINDSPEED80M'])
#make sure htat the index of the dataframe is a timestamp
ts_df = ts_df.set_index('Time')
c.datapoints.insert_dataframe(ts_df)

####Create sequence
seq = c.sequences.create(Sequence(name='HUMBOLDT_BAY:FORECAST_WIND',
                                  external_id='HUMBOLDT_BAY:FORECAST_WIND',
                                  asset_id=6352781722863707,
                                  data_set_id=data_set_id,
                                  columns = [
                                      {
                                        'external_id': 'FORECAST_TIMESTAMP', 
                                        'name': 'FORECAST_TIMESTAMP',  
                                        'valueType': 'String'
                                    },
                                      {
                                          'external_id': 'FORECAST-WINDSPEED80M',
                                          'name': 'FORECAST-WINDSPEED80M',
                                          'valueType': 'Double'
                                          },
                                      {
                                          'external_id': 'DATE_FORECAST_CREATED',
                                          'name': 'DATE_FORECAST_CREATED',
                                          'valueType': 'String'
                                          }
                                      ]))
#upload data to sequence
#Make sure that the column names match the external_id of the columns 
#defined in the sequence.
seq_df = pd.DataFrame(columns=['FORECAST_TIMESTAMP', 'FORECAST-WINDSPEED80M, DATE_FORECAST_CREATED'])
c.sequences.data.insert_dataframe(seq_df, id=seq.id)
