# --- SETUP --- #

import os

import numpy as np
import pandas as pd

from cognite.client import CogniteClient
from cognite.client.data_classes import Asset

# Create a function to make turbine assets more easily
def make_asset(parent_name, asset_name, **kwargs):
    prefix = ":".join(parent_name.split(":")[:2])
    full_name = prefix + ":" + asset_name
    asset = Asset(
        name = full_name.capitalize(),
        external_id = full_name.upper(),
        parent_external_id = parent_name.upper(),
        **kwargs
    )
    return asset

# Specify parameters for assets to be created
args_lst = [
    # Each entry should be of the following format:
    # ([parent_asset_external_ID, asset_name], {additional_keyward_args})
    (["unknown", "turbine_1"], {}),
    # Rotor components
    (["unknown:turbine_1", "rotor"], {}),
    (["unknown:turbine_1:rotor", "blades"], {}),
    (["unknown:turbine_1:blades", "blade_A"], {}),
    (["unknown:turbine_1:blades", "blade_B"], {}),
    (["unknown:turbine_1:blades", "blade_C"], {}),
    (["unknown:turbine_1:rotor", "hub"], {}),
    (["unknown:turbine_1:hub", "pitch_bearing"], {}),
    (["unknown:turbine_1:rotor", "spinner"], {}),
    # Nacelle components
    (["unknown:turbine_1", "nacelle"], {}),
    (["unknown:turbine_1:nacelle", "drivetrain"], {}),
    (["unknown:turbine_1:nacelle", "yaw_system"], {}),
    (["unknown:turbine_1:drivetrain", "main_bearing"], {}),
    (["unknown:turbine_1:main_bearing", "front_bearing"], {}),
    (["unknown:turbine_1:main_bearing", "rear_bearing"], {}),
    (["unknown:turbine_1:drivetrain", "low-speed_shaft"], {}),
    (["unknown:turbine_1:drivetrain", "gearbox"], {}),
    (["unknown:turbine_1:gearbox", "main_carrier"], {}),
    (["unknown:turbine_1:drivetrain", "brake"], {}),
    (["unknown:turbine_1:drivetrain", "high-speed_shaft"], {}),
    (["unknown:turbine_1:drivetrain", "generator"], {}),
    (["unknown:turbine_1:generator", "stator"], {}),
    (["unknown:turbine_1:drivetrain", "controller"], {}),
    (["unknown:turbine_1:controller", "anemometer"], {}),
    (["unknown:turbine_1:controller", "remote_terminal_unit"], {}),
    (["unknown:turbine_1:drivetrain", "bedplate"], {}),
    # Tower components
    (["unknown:turbine_1", "tower"], {}),
    (["unknown:turbine_1:tower", "converter"], {}),
    (["unknown:turbine_1:converter", "inverter"], {}),
    (["unknown:turbine_1:converter", "rectifier"], {}),
    (["unknown:turbine_1:tower", "transformer"], {})
]

# --- MAIN --- #

def main():
    # Connect to server
    client = CogniteClient(
        client_name="sangyoon.park",
        project="cec",
        api_key=os.environ.get("API_KEY_CDF_CEC")
    )

    # Check login status
    print(client.login.status())

    # Create a farm-level root node
    client.assets.create(Asset(name="Unknown", external_id="UNKNOWN"))

    # Create turbine assets in CDF
    turbine_assets = [make_asset(*args, **kwargs) for args, kwargs in args_lst]
    client.assets.create_hierarchy(turbine_assets)

if __name__ == "__main__":
    main()
