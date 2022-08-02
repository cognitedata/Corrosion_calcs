from cognite.client import CogniteClient
from getpass import getpass
import pandas as pd

#set variables
file = 'G:/Shared drives/Customers/Aker Solutions/CEC California Energy Commission/01 Data/Engie French Data/TurbineData.csv'
# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                  client_name = 'marissa.pang',
                  project = 'cec')

df = pd.read_csv(file, delimiter=';')
df = df.fillna('')
rows = df.to_dict("index")

res = c.raw.rows.insert("Engie_OpenData", "LA_HAUTE_BORNE_TURBINE", rows)
