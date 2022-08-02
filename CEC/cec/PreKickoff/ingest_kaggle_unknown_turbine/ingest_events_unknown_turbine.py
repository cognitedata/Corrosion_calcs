# The data was obtained on 06/24/2020 from:
# https://www.kaggle.com/wasuratme96/iiot-data-of-wind-turbine

import os
from datetime import datetime, timedelta
from getpass import getpass

import numpy as np
import pandas as pd

from cognite.client import CogniteClient
from cognite.client.data_classes import Event


# Map status code to assets
asset_code_map = {307: 'blade',
                  72:'blade',
                  71:'turbine',
                  3:'turbine',
                  304:'inverter',
                  31:'tower',
                  66:'inverter',
                  42:'blade',
                  15:'turbine',
                  22:'yaw_system',
                  26:'inverter',
                  301:'controller',
                  67:'inverter',
                  206:'inverter',
                  204:'inverter',
                  9:'generator',
                  17:'turbine',
                  60:'tower',
                  21:'turbine',
                  220:'tower',
                  1:'turbine',
                  228:'turbine',
                  240:'controller',
                  222:'turbine',
                  8:'turbine',
                  80:'tower',
                  62:'tower',
                  2:'turbine',
                  0:'turbine'}


def main():
    # Connect to server
    c = CogniteClient(api_key=getpass("API-KEY: "),
                      client_name = 'yutong.zhou',
                      project = 'cec')

    # Check login status
    print(c.login.status())

    # Read in data
    status = pd.read_csv('./data/status_data.csv')

    # Convert time string to milliseconds
    status['Time'] =  pd.to_datetime(status['Time'], format='%d/%m/%Y %H:%M:%S').astype(np.int64)/int(1e6)

    # Construct type and subtype based on status text
    for index, row in status.iterrows():
        if ':' in row['Status Text']:
            type_subtype = row['Status Text'].split(':', 1)
            status.loc[index, 'Type'] = type_subtype[0]
            status.loc[index, 'Subtype'] = type_subtype[1]
        else:
            status.loc[index, 'Type'] = row['Status Text']
            status.loc[index, 'Subtype'] = 'N/A'

    for index, row in status.iterrows():
        status.loc[index, 'Asset'] = asset_code_map[row['Main Status']]

    # Map assets to the corresponding external ids
    for index, row in status.iterrows():
        if row['Asset'] == 'turbine':
            status.loc[index, 'ExternalId'] = 'UNKNOWN:TURBINE_1'
        else:
            status.loc[index, 'ExternalId'] = 'UNKNOWN:TURBINE_1:'+row['Asset'].upper()

    # Create events
    events = []
    for index, row in status.iterrows():
        events.append(Event(external_id=row['ExternalId']+':EVENT_'+str(index),
                            data_set_id=615945337399135,
                            start_time=row['Time'], end_time=row['Time'],
                            type=row['Type'], subtype=row['Subtype'],
                            description=row['Status Text'],
                            asset_ids=[c.assets.retrieve(external_id=row['ExternalId']).id],
                            metadata={'Main Status':row['Main Status'],
                                      'Sub Status':row['Sub Status'],
                                      'T':row['T'],
                                      'Service':row['Service'],
                                      'Fault Msg':row['FaultMsg'],
                                      'Value':row['Value0']}))

    # Put events into CDF
    c.events.create(events)


if __name__ == "__main__":
    main()
