from getpass import getpass

import numpy as np
import pandas as pd
import datetime as datetime

from cognite.client import CogniteClient
from cognite.client.data_classes import Asset
from cognite.client.data_classes import TimeSeries
from cognite.client.data_classes import AssetUpdate

# Connect to server
c = CogniteClient(api_key=getpass('Enter API-Key:'),
                  client_name='yanyu.zhong',
                  project='cec')

# Check login status
c.login.status()

# Load data description
data_description = pd.read_csv(r"C:\Users\Lenovo\Desktop\data_description.csv")
col_des = list(data_description.columns)[0].split(";")
des = []
data_des = pd.DataFrame(des, columns=col_des)
datapoints_des = []
for idx, row in data_description.iterrows():
    datapoints_des.append(list(row)[0].split(";"))
dataseries_des = []
for row in datapoints_des:
    dataseries_des.append(pd.Series(row, index=data_des.columns))
data_des = data_des.append(dataseries_des, ignore_index=True)
data_des = data_des.drop(data_des[data_des["Variable_name"] == "Pas"].index)
data_des = data_des.reset_index(drop=True)

# Setup the dataset to be frontfilled (same process as before)
# Read Data from csv file
wind_data = pd.read_csv(r"C:\Users\Lenovo\Desktop\turbineData.csv")
wind_data.head()
newCol = list(wind_data.columns)[0].split(";")
# Create new pandas dataframe with the split columns
data = []
new_wind_data = pd.DataFrame(data, columns=newCol)
# Split all datapoints in wind_data
datapoints = []
for idx, row in wind_data.iterrows():
    datapoints.append(list(row)[0].split(";"))
dataseries = []
for row in datapoints:
    dataseries.append(pd.Series(row, index=new_wind_data.columns))
modified_wind_data = new_wind_data.append(dataseries, ignore_index=True)
# Select columns with average value
newCols = list(filter(lambda string: "avg" in string, newCol))
newCols.insert(0, "Date_time")
newCols.insert(0, "Wind_turbine_name")
newCols.remove('Pas_avg')
selectedDatapoints = pd.DataFrame(modified_wind_data[newCols])
# Convert string to float
for i in newCols[2:]:
    selectedDatapoints[i] = pd.to_numeric(selectedDatapoints[i])
# Convert json datetime to miliseconds
num = 3
updateTime = selectedDatapoints["Date_time"]
print(updateTime)
for i in range(len(updateTime)):
    temp = updateTime.iloc[i]
    updateTime[i] = datetime.datetime.strptime(temp[:-6], '%Y-%m-%dT%H:%M:%S')
    updateTime[i] = updateTime[i].timestamp() * 1000 + 31536000000 * \
        num  # Add num year to the time range
# Filter timestamp until current time
newselected = pd.DataFrame(
    selectedDatapoints.loc[selectedDatapoints["Date_time"] <= datetime.datetime.now().timestamp() * 1000])
selectedDatapoints = newselected
# Replace NaN with average of the column
selectedDatapoints = selectedDatapoints.fillna(selectedDatapoints.mean())

# Split the dataset into four different subsets with four different wind turbines
turbine1 = pd.DataFrame(
    selectedDatapoints.loc[selectedDatapoints["Wind_turbine_name"] == "R80711"])
turbine2 = pd.DataFrame(
    selectedDatapoints.loc[selectedDatapoints["Wind_turbine_name"] == "R80790"])
turbine3 = pd.DataFrame(
    selectedDatapoints.loc[selectedDatapoints["Wind_turbine_name"] == "R80736"])
turbine4 = pd.DataFrame(
    selectedDatapoints.loc[selectedDatapoints["Wind_turbine_name"] == "R80721"])
turbines = [turbine1, turbine2, turbine3, turbine4]

turbineNames = {"_R80721": turbine4, "_R80711": turbine1,
                "_R80790": turbine2, "_R80736": turbine3}

# Frontfill the dataset
for turbineName in turbineNames:
    rename_cols = {}
    for col in newCols[2:]:
        n = data_des[data_des["Variable_name"] ==
                     col[:-4]].Variable_long_name.iloc[0]
        name = "France:"+n+turbineName
        rename_cols[col] = c.time_series.retrieve(external_id=name).id
    new = turbineNames[turbineName].rename(columns=rename_cols)
    new = new.set_index('Date_time')
    new = new.drop(columns=["Wind_turbine_name"])
    # Put the time series into CDF
    c.datapoints.insert_dataframe(new)
