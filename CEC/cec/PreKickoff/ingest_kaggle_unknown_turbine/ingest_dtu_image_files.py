# The image files were obtained on 07/06/2020 from:
# https://data.mendeley.com/datasets/hd96prn3nc/1


# --- SET UP --- #
from cognite.client import CogniteClient
from getpass import getpass

# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                  client_name = 'yutong.zhou',
                  project = 'cec')

# Check login status
print(c.login.status())

# Upload Nordtank 2017 files
c.files.upload("./DTU/Nordtank_2017",
               source="Nordtank_2017",
               mime_type="image/jpeg",
               asset_ids=[2877216287093309],
               recursive=True,
               metadata={"Source": "https://data.mendeley.com/datasets/hd96prn3nc/1#folder-0b65f309-ff9c-48da-9f52-687990a5483e"})

# Upload Nordtank 2018 files
c.files.upload("./DTU/Nordtank_2018",
               source="Nordtank_2018",
               mime_type="image/jpeg",
               asset_ids=[2877216287093309],
               recursive=True,
               metadata={"Source": "https://data.mendeley.com/datasets/hd96prn3nc/1#folder-0b65f309-ff9c-48da-9f52-687990a5483e"})
