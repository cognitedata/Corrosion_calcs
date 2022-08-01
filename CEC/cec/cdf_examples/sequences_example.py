#import packages
from cognite.client import CogniteClient
from cognite.client.data_classes import TimeSeries, Sequence
import pandas as pd
from getpass import getpass
import datetime

# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                  client_name = 'edrmedeso',
                  project = 'cec')
#create variables
external_id = 'HUMBOLDT_BAY:TURBINE_1:TOWER:BOTTOM_WELD'
data_set_id = 7751435616395347
#retrieve asset
asset = c.assets.retrieve(external_id=external_id)


####Create sequence
seq = c.sequences.create(Sequence(name='example',
                                  external_id='example',
                                  asset_id=asset.id,
                                  data_set_id=data_set_id,
                                  columns = [
                                      {
                                        'external_id': 'example:column_1', 
                                        'name': 'example:column_1',  
                                        'valueType': 'String'
                                    },
                                      {
                                          'external_id': 'example:column_2',
                                          'name': 'example:column_2',
                                          'valueType': 'Double'
                                          }
                                      ]))
#upload data to sequence
#Make sure that the column names match the external_id of the columns 
#defined in the sequence.
seq_df = pd.DataFrame(columns=['example:column_1', 'example:column_2'])
c.sequences.data.insert_dataframe(seq_df, id=seq.id)
