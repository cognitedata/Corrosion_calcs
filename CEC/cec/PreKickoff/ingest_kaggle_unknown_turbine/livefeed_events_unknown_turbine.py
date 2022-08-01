# --- SETUP --- #
from cognite.experimental import CogniteClient
import pandas as pd
from getpass import getpass
import numpy as np
from cognite.client.data_classes import Event
from datetime import datetime
import pytz
import time
from ingest_events_unknown_turbine import asset_code_map
from frontfill_events_unknown_turbine import preprocess_events

# --- MAIN --- #
# Connect to server
c = CogniteClient(api_key=getpass("API-KEY: "),
                    client_name = 'yutong.zhou',
                    project = 'cec')

# Check login status
print(c.login.status())

# Select the subset of data that will be looped
status, looped_data = preprocess_events()

data = looped_data.copy()
input_data = data.to_dict()

# Implement live streaming function
def handle(client, data):
    import time
    import pandas as pd
    import numpy as np
    from cognite.client.data_classes import Event
    from datetime import datetime, timedelta
    import pytz
    from dateutil.relativedelta import relativedelta


    # generate new events
    interval=600000
    datetime_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    ms_now = int(round(time.time() * 1000))
    events_now = []
    offset = datetime_now.year - 2014
    for key, value in data['Time'].items():
        data['Time'][key] = datetime.strptime(value,'%Y-%m-%d %H:%M:%S%z')
        data['Time'][key] = data['Time'][key] + relativedelta(years=offset)
        data['Time_ms'][key] = int(data['Time'][key].timestamp() * 1000)
        if (data['Time_ms'][key] <= ms_now) and ((ms_now - 2 * interval) < data['Time_ms'][key]):
            events_now.append(key)

    # check existing events
    existing_events = len(client.events.list(limit=None))

    # create events
    events = []
    for event in events_now:
        events.append(Event(external_id=data['ExternalId'][event]+":EVENT_"+str(existing_events),
                            data_set_id=615945337399135,
                            start_time=data['Time_ms'][event], end_time=data['Time_ms'][event],
                            type=str(data['Type'][event]), subtype=str(data['Subtype'][event]),
                            description=str(data['Status Text'][event]),
                            asset_ids=[c.assets.retrieve(external_id=row['ExternalId']).id],
                            metadata={"Main Status":str(data['Main Status'][event]),
                                  "Sub Status":str(data['Sub Status'][event]),
                                  "T":str(data['T'][event]),
                                  "Service":str(data['Service'][event]),
                                  "Fault Msg":str(data['FaultMsg'][event]),
                                  "Value":str(data['Value0'][event])}))
        existing_events += 1
    client.events.create(events)
    return {
        "number of events created": len(events)
    }


# Deploy the function
external_id = "Unknown:turbine_1:func:events_livefeed"
try:
    c.functions.delete(external_id=external_id)
except:
    pass
function = c.functions.create(
    name = external_id,
    external_id=external_id,
    function_handle = handle,
    api_key = api_key)

# Setup schedule
schedule = c.functions.schedules.create(
    name = external_id,
    function_external_id=external_id,
    cron_expression = "*/10 * * * *",
    data=input_data
)
