# -*- coding: utf-8 -*-

#import packages
from getpass import getpass
from cognite.client import CogniteClient
from cognite.client.data_classes import TimeSeries

#define variables
data_set_id = 1319557029992498
extid_prefix = 'bird_detection_jp:'
name_prefix = 'Bird Detection: '
desc_suffix = ' data from Japan use case'

#connect to cdf
c = CogniteClient(api_key=getpass("API-KEY: "), client_name="marissa.pang", project="cec")

#create timeseries
bird_count = TimeSeries(external_id = extid_prefix + 'bird_count', 
                        name = name_prefix + 'Bird Count',
                        description = name_prefix + 'Bird Count' + desc_suffix,
                        data_set_id=data_set_id)

confidence = TimeSeries(external_id = extid_prefix + 'confidence', 
                        name = name_prefix + 'Confidence',
                        description = name_prefix + 'Confidence' + desc_suffix,
                        data_set_id=data_set_id)

bounding_box = TimeSeries(external_id = extid_prefix + 'bounding_box_size', 
                        name = name_prefix + 'Bounding Box Size',
                        description = name_prefix + 'Bounding Box Size' + desc_suffix,
                        data_set_id=data_set_id)

ts_list = [bird_count, confidence, bounding_box]

ts_create = c.time_series.create(ts_list)
