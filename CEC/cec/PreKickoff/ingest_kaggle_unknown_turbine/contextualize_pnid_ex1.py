import os
import time
import urllib

import numpy as np
import pandas as pd

from cognite.experimental import CogniteClient


# Connect to server
client = CogniteClient(
    client_name="sangyoon.park",
    project="cec",
    api_key=os.environ.get("API_KEY_CDF_CEC")
)

# Check login status
print(client.login.status())

# Specify path to data
PATH_TO_DATA = "./data/"

# Upload P&ID file (PDF) to CDF
client.files.upload(
    PATH_TO_DATA + "pnid_ex1.pdf",
    external_id="UNKNOWN:TURBINE_1:PNID_EX1.PDF",
    name="Unknown:turbine_1:pnid_ex1.pdf",
    source="sangyoon.park",
    mime_type="application/pdf",
    asset_ids=[client.assets.retrieve(external_id="UNKNOWN:TURBINE_1").id], # Put it at turbine level
    metadata={"Description" : "Prototype P&ID created by Sangyoon Park on 07/16/2020"},
)

# Parse and contextualize P&ID
job = client.pnid_parsing.parse(
    file_id=client.files.retrieve(external_id="UNKNOWN:TURBINE_1:PNID_EX1.PDF").id,
    entities=[
        # Put asset names to match
        "Unknown:turbine_1:blade_a",
        "Unknown:turbine_1:blade_b",
        "Unknown:turbine_1:blade_c",
        "Unknown:turbine_1:rotor",
        "Unknown:turbine_1:gearbox",
        "Unknown:turbine_1:generator",
        "Unknown:turbine_1:rectifier",
        "Unknown:turbine_1:inverter",
        "Unknown:turbine_1:transformer",
        "Unknown:turbine_1:controller",
    ],
    partial_match=True,
)

# Get job results
result = job.result
matched_names = [item_dict.get("text") for item_dict in result["items"] if item_dict.get("text")]
matched_ids = [client.assets.retrieve(external_id=name.upper()).id for name in matched_names]

# Download parsed SVG file
urllib.request.urlretrieve(result["svgUrl"], PATH_TO_DATA + "pnid_ex1.svg")

# Upload parsed P&ID file (SVG) to CDF
client.files.upload(
    PATH_TO_DATA + "pnid_ex1.svg",
    external_id="UNKNOWN:TURBINE_1:PNID_EX1.SVG",
    name="Unknown:turbine_1:pnid_ex1.svg",
    source="contextualization",
    mime_type="image/svg+xml",
    asset_ids=matched_ids,
    overwrite=True,
    metadata={"Description" : "Prototype P&ID created by Sangyoon Park on 07/16/2020"},
)
