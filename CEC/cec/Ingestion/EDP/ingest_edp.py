# -*- coding: utf-8 -*-
# import packages
from cognite.client import CogniteClient
from getpass import getpass
import pandas as pd
from datetime import datetime
import time
from cognite.client.data_classes import Asset, TimeSeries, Event
from cognite.client.utils import timestamp_to_ms
# set variables
data_set_id = 3371785641358847
# folder = 'C:/Users/MarissaPang/Documents/CEC/Data/PODRequesrt_5129/1Hz-Tur/'
variables = 'C:/Users/MarissaPang/Documents/CEC/Data/wind-farm-1-asset ts contextualization.xlsx'
db = 'EDP'
# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                  client_name = 'marissa.pang',
                  project = 'cec')

# read in variables table
vardf = pd.read_excel(variables)
vardf['Asset'] = vardf.Asset.str.upper().str.replace(' ', '_')
# create parent asset
asset = Asset(
    external_id = 'EDP',
    name = 'EDP',
    data_set_id = data_set_id)
parent = c.assets.create(asset)
#read in data tables table by table
tables = c.raw.tables.list(db_name=db, limit=None).to_pandas()
for tbl in tables['name']:
    print(tbl)
    df = c.raw.rows.list(db_name=db, table_name=tbl, limit=None).to_pandas()
    # create children assets for turbines
    if 'Turbine_ID' in df.columns:
        turbinecol = 'Turbine_ID'
    elif 'UnitTitle' in df.columns:
        turbinecol = 'UnitTitle'
    else:
        turbinecol = 'skip'
    if turbinecol == 'skip':
        next
    else:
        asset_list = df[turbinecol].apply(lambda x: Asset(
            external_id = 'EDP:Turbine_' + x.strip(),
            name = 'EDP:Turbine_' + x.strip(),
            data_set_id = data_set_id,
            parent_id = parent.id)).tolist()
        #filter out turbines already in cdf
        time.sleep(10)
        cdf_turbines = c.assets.list(data_set_ids = [data_set_id], limit = None).to_pandas()
        asset_list = [t for t in asset_list if t.external_id not in cdf_turbines.externalId.tolist()]
        turbines = c.assets.create(asset_list)
    if tbl.split('-')[3] in ['failures', 'logs']:
        # create assets if they don't already exist first
        if tbl.split('-')[3] in ['failures']:
            asset_list = df[[turbinecol, 'Component']].drop_duplicates().apply(lambda x: Asset(
                external_id = 'EDP:' + x.Component.strip() + '_' + x[turbinecol].strip(),
                name = 'EDP:' + x.Component.strip() + '_' + x[turbinecol].strip(),
                data_set_id = data_set_id,
                parent_external_id = 'EDP:Turbine_' + x[turbinecol].strip()),
                axis = 1).tolist()
            asset_list = [t for t in asset_list if t.external_id  not in cdf_turbines.externalId.tolist()]
            components = c.assets.create(asset_list)
            cdf_turbines = cdf_turbines.append(components.to_pandas())
            df['ext_id'] = df.Component.str.strip() + '_' + df[turbinecol].str.strip()
        else:
            df['ext_id'] = df[turbinecol].str.strip()
            df = df.rename(columns={'TimeDetected': 'Timestamp', 'Remark': 'Remarks'})
        # create events 
        event_list = df.apply(lambda x: Event(
            external_id = 'EDP:' + x.ext_id + ':' + tbl.split('-')[3] + '_' + tbl.split('-')[-1] + '_' + x.Timestamp.strip(),
            data_set_id = data_set_id,
            start_time = timestamp_to_ms(datetime.strptime(x.Timestamp, '%Y-%m-%dT%H:%M:%S+00:00')),
            end_time = timestamp_to_ms(datetime.strptime(x.Timestamp, '%Y-%m-%dT%H:%M:%S+00:00')),
            type = tbl.split('-')[3],
            subtype = tbl.split('-')[-1],
            description = x.Remarks,
            # metadata = ,
            asset_ids = cdf_turbines.loc[cdf_turbines.externalId == 'EDP:' + x.ext_id, 'id'].tolist(),
            source = 'EDP'),
            axis = 1).tolist()
        events = c.events.create(event_list)
    elif tbl.split('-')[3] in ['signals']:
        varsubdf = vardf[vardf['Data files'].apply(lambda x: tbl in x)]
        assert(len(varsubdf) == len(df.columns)-2)
        # create assets if they don't already exist first
        alist = [t for t in varsubdf.Asset.unique() if t != 'TURBINE']
        for a in alist:
            asset_list = df[turbinecol].drop_duplicates().apply(lambda x: Asset(
                external_id = 'EDP:' + a + '_' + x.strip(),
                name = 'EDP:' + a + '_' + x.strip(),
                data_set_id = data_set_id,
                parent_external_id = 'EDP:Turbine_' + x.strip())).tolist()
            asset_list = [t for t in asset_list if t.external_id  not in cdf_turbines.externalId.tolist()]
            components = c.assets.create(asset_list)
            cdf_turbines = cdf_turbines.append(components.to_pandas())
        for tb in df[turbinecol].unique():
            # create time series
            varsubdf.loc[varsubdf.Asset == 'TURBINE', 'Asset'] = varsubdf.loc[varsubdf.Asset == 'TURBINE', 'Asset'].str.title()
            ts_list = varsubdf.apply(lambda x: TimeSeries(
                external_id = 'EDP:' + tb.strip() + '_' + x['Time Series'] + ':' + tbl.split('-')[-1],
                name = 'EDP:' + tb.strip() + '_' + x['Time Series'] + ':' + tbl.split('-')[-1],
                asset_id = cdf_turbines.loc[cdf_turbines.externalId == 'EDP:' + x['Asset'] + '_' + tb.strip(), 'id'].item(),
                data_set_id = data_set_id),
                axis = 1).tolist()
            timeseries = c.time_series.create(ts_list)
            # insert data
            temp_df = df.loc[df[turbinecol] == tb, varsubdf['Time Series'].tolist() + ['Timestamp']]
            temp_df = temp_df.set_index('Timestamp')
            temp_df = temp_df.rename(columns = {t: 'EDP:' + tb.strip() + '_' + t + ':' + tbl.split('-')[-1] for t in varsubdf['Time Series']})
            temp_df.index = pd.to_datetime(temp_df.index)
            temp_df = temp_df.apply(pd.to_numeric)
            dps = c.datapoints.insert_dataframe(temp_df, external_id_headers = True, dropna = True)
    else:
        varsubdf = vardf[vardf['Data files'].apply(lambda x: tbl in x)]
        assert(len(varsubdf) == len(df.columns)-1)
        # create assets if they don't already exist first
        asset_list = varsubdf['Asset'].drop_duplicates().apply(lambda x: Asset(
            external_id = 'EDP:' + x.strip(),
            name = 'EDP:' + x.strip(),
            data_set_id = data_set_id,
            parent_external_id = 'EDP')).tolist()
        asset_list = [t for t in asset_list if t.external_id  not in cdf_turbines.externalId.tolist()]
        components = c.assets.create(asset_list)
        cdf_turbines = cdf_turbines.append(components.to_pandas())
        # create time series
        ts_list = varsubdf.apply(lambda x: TimeSeries(
            external_id = 'EDP:' + x['Time Series'] + ':' + tbl.split('-')[-1],
            name = 'EDP:' + x['Time Series'] + ':' + tbl.split('-')[-1],
            asset_id = cdf_turbines.loc[cdf_turbines.externalId == 'EDP:' + x['Asset'], 'id'].item(),
            data_set_id = data_set_id),
            axis = 1).tolist()
        timeseries = c.time_series.create(ts_list)
        # insert data
        df = df.set_index('Timestamp')
        df = df.rename(columns = {t: 'EDP:' + t + ':' + tbl.split('-')[-1] for t in varsubdf['Time Series']})
        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric)
        dps = c.datapoints.insert_dataframe(df, external_id_headers = True, dropna = True)
            