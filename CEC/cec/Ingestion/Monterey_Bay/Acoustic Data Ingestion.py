# -*- coding: utf-8 -*-
#import packages
from cognite.client import CogniteClient
from getpass import getpass
import pandas as pd
from google.cloud import storage
import scipy.io, os
from cognite.client.data_classes import Asset

#set variables
data_set_id = 7683216303780148
file = 'https://storage.cloud.google.com/noaa-passive-bioacoustic/sanctsound/mb02/03/metadata/SanctSound_MB02_03.json'
matfile = 'C:/Users/MarissaPang/Downloads/sanctsound_mb02_01_ancillary_temperature_MB01_01_RBRsT_101566.mat'
# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                  client_name = 'marissa.pang',
                  project = 'cec')

# Instantiate a Google Cloud Storage client and specify required bucket and file
storage_client = storage.Client.from_service_account_json(
        'C:/Users/MarissaPang/Documents/CEC/marissapang-78b5ddcfc9dd.json')
bucket = storage_client.get_bucket('noaa-passive-bioacoustic')
blobs = bucket.list_blobs('sanctsound/mb02')
#df = pd.read_json(bucket.blob('sanctsound/mb02/01/metadata/SanctSound_MB02_01.json').download_as_string(client=None))

# mat = scipy.io.loadmat(matfile)
# mdata = mat['RSK']
# mdtype = mdata.dtype  # dtypes of structures are "unsized objects"
# * SciPy reads in structures as structured NumPy arrays of dtype object
# * The size of the array is the size of the structure array, not the number
#   elements in any particular field. The shape defaults to 2-dimensional.
# * For convenience make a dictionary of the data using the names from dtypes
# * Since the structure has only one element, but is 2-D, index it at [0, 0]
# ndata = {n: mdata[n][0, 0] for n in mdtype.names}
# Reconstruct the columns of the data table from just the time series
# Use the number of intervals to test if a field is a column or metadata
# columns = [n for n, v in ndata.iteritems() if v.size == ndata['numIntervals']]
# now make a data frame, setting the time stamps as the index
# df = pd.DataFrame(np.concatenate([ndata[c] for c in columns], axis=1),
#                   index=[datetime(*ts) for ts in ndata['timestamps']],
#                   columns=columns)



#Create parent asset for Monterey Bay
asset = Asset(
    external_id = 'MONTEREY_BAY',
    name = 'Monterey Bay',
    data_set_id = data_set_id)
res = c.assets.create(asset)
#Create asset for Deployment
asset = Asset(
    external_id = 'SANCTSOUND_MB02',
    name = 'SanctSound_MB02',
    parent_id = res.id,
    parent_external_id = res.external_id,
    data_set_id = data_set_id)
deployment_asset = c.assets.create(asset)
#Create asset for Sensors
asset = Asset(
    external_id = 'SANCTSOUND_MB02_01',
    name = 'SANCTSOUND_MB02_01',
    parent_id = deployment_asset.id,
    parent_external_id = deployment_asset.external_id,
    data_set_id = data_set_id
    # metadata = {
    #     'DEPLOYMENT_ID': '01',
    #     'DEPLOYMENT_ALIAS': 'SanctSound_MB02_01_671903780_20181115',
    #     'INSTRUMENT_TYPE': 'SoundTrap 500',
    #     'INSTRUMENT_ID': '671903780',
    #     "DEPLOYMENT_TIME": "2018-11-15T18:44:09", 
    #     "AUDIO_START": "2018-11-15T19:00:09", 
    #     "RECOVERY_TIME": "2019-04-08T18:17:09", 
    #     "AUDIO_END": "2019-04-07T10:50:09", 
    #     "DEPLOY_SHIP": "R/V Fulmar", 
    #     "DEPLOY_INSTRUMENT_DEPTH": "-64.5", 
    #     "DEPLOY_BOTTOM_DEPTH": "-68", 
    #     "RECOVER_LAT": "36.6495", 
    #     "RECOVER_LON": "-121.9084", 
    #     "RECOVER_SHIP": "NOAA's R/V R4107", 
    #     "RECOVER_INSTRUMENT_DEPTH": "-64.5", 
    #     "RECOVER_BOTTOM_DEPTH": "-68"
    #     }
    )
sensor_1_asset = c.assets.create(asset)

sensor_1_asset = c.assets.retrieve(external_id='SANCTSOUND_MB02_01')
#upload files for sensor
for blob in bucket.list_blobs(prefix='sanctsound/mb02/01/audio/'):
    file_name = blob.name.split('/')[-1]
    if  c.files.retrieve(external_id = file_name) != None:
        # 'already exists'
        next
    else:
        print(blob.name)
        local_file = 'C:/Users/MarissaPang/Documents/CEC/temp/' + file_name
        blob.download_to_filename(local_file)
        print('downloaded')
        c.files.upload(
            path = local_file,
            external_id = file_name,
            name = file_name,
            source = 'NOAA Passive Acoustic Data',
            mime_type = 'audio/wav',
            asset_ids = [sensor_1_asset.id],
            data_set_id = data_set_id
            )
        print('uploaded')
        os.remove(local_file)
        print('deleted')
