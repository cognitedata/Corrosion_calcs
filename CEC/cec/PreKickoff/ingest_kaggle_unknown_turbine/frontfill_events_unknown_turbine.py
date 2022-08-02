# The data was obtained on 06/24/2020 from:
# https://www.kaggle.com/wasuratme96/iiot-data-of-wind-turbine

import os
from datetime import datetime, timedelta
from getpass import getpass

import numpy as np
import pandas as pd

from cognite.client import CogniteClient
from cognite.client.data_classes import Event

from ingest_events_unknown_turbine import asset_code_map


def preprocess_events():
    # Read in data
    status = pd.read_csv('./data/status_data.csv')

    # Convert time string to milliseconds
    status['Time'] = pd.to_datetime(status['Time'], format='%d/%m/%Y %H:%M:%S').dt.tz_localize('US/Central').dt.tz_convert('UTC')
    status['Time_ms'] = pd.to_datetime(status['Time'], format='%Y-%m-%d %H:%M:%S').astype(np.int64)/int(1e6)

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

    # Select the subset of data that will be looped
    looped_data = status[status['Time_ms'] >= 1398748699000]

    return status, looped_data

def main():
    # Connect to server
    c = CogniteClient(api_key=getpass("API-KEY: "),
                      client_name = 'yutong.zhou',
                      project = 'cec')

    # Check login status
    print(c.login.status())

    # Select the subset of data that will be looped
    status, looped_data = preprocess_events()

    # Loop the selected data for each year (2015-2021)
    status_2015_2016 = looped_data.copy()
    status_2015_2016['Time'] = pd.to_datetime(status_2015_2016['Time'],
                                              format='%d/%m/%Y %H:%M:%S') + \
                                              pd.offsets.DateOffset(years=1)
    status_2015_2016['Time_ms'] = pd.to_datetime(status_2015_2016['Time'],
    format='%Y-%m-%d %H:%M:%S').astype(np.int64)/int(1e6)

    status_2016_2017 = looped_data.copy()
    status_2016_2017['Time'] = pd.to_datetime(status_2016_2017['Time'],
                                              format='%d/%m/%Y %H:%M:%S') + \
                                              pd.offsets.DateOffset(years=2)
    status_2016_2017['Time_ms'] = pd.to_datetime(status_2016_2017['Time'],
    format='%Y-%m-%d %H:%M:%S').astype(np.int64)/int(1e6)

    status_2017_2018 = looped_data.copy()
    status_2017_2018['Time'] = pd.to_datetime(status_2017_2018['Time'],
                                              format='%d/%m/%Y %H:%M:%S') + \
                                              pd.offsets.DateOffset(years=3)
    status_2017_2018['Time_ms'] = pd.to_datetime(status_2017_2018['Time'],
    format='%Y-%m-%d %H:%M:%S').astype(np.int64)/int(1e6)

    status_2018_2019 = looped_data.copy()
    status_2018_2019['Time'] = pd.to_datetime(status_2018_2019['Time'],
                                              format='%d/%m/%Y %H:%M:%S') + \
                                              pd.offsets.DateOffset(years=4)
    status_2018_2019['Time_ms'] = pd.to_datetime(status_2018_2019['Time'],
    format='%Y-%m-%d %H:%M:%S').astype(np.int64)/int(1e6)

    status_2019_2020 = looped_data.copy()
    status_2019_2020['Time'] = pd.to_datetime(status_2019_2020['Time'],
                                              format='%d/%m/%Y %H:%M:%S') + \
                                              pd.offsets.DateOffset(years=5)
    status_2019_2020['Time_ms'] = pd.to_datetime(status_2019_2020['Time'],
    format='%Y-%m-%d %H:%M:%S').astype(np.int64)/int(1e6)

    status_2020_2021 = looped_data.copy()
    status_2020_2021['Time'] = pd.to_datetime(status_2020_2021['Time'],
                                              format='%d/%m/%Y %H:%M:%S') + \
                                              pd.offsets.DateOffset(years=6)
    status_2020_2021['Time_ms'] = pd.to_datetime(status_2020_2021['Time'],
    format='%Y-%m-%d %H:%M:%S').astype(np.int64)/int(1e6)

    # Concatenate the above dataframes
    frontfill_status = pd.concat([status, status_2015_2016, status_2016_2017,
                                  status_2017_2018, status_2018_2019,
                                  status_2019_2020, status_2020_2021],
                                  ignore_index=True)

    # Create events
    events = []
    for index, row in frontfill_status.iterrows():
        print(index)
        events.append(Event(external_id=row['ExternalId']+':EVENT_'+str(index), data_set_id=615945337399135,
                            start_time=row['Time_ms'], end_time=row['Time_ms'],
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
