# French Turbine Data Ingestion

### `/anomaly_detection_template.py`

This is a template for anomaly detection using [the Prophet library](https://github.com/facebook/prophet), deployed as a Cognite function.

### `/frontfill_french_turbine.py`

This is the script to frontfill french turbine to current date by repeating the data from 2017 to 2018.

### `/ingest_engie_renewables_data.py`

This is the script to ingest the turbine data obtained from Engie.

### `/live_feed_french_turbine_timeseries.py`

This is the script to feed live turbine data to CDF using real data from previous years. This is deployed as a Cognite function.

### `/live_feed_performance_timeseries_french_turbine.py`

This is the script to create and feed live performance data for each turbine. Here we are only including the code for `turbine_80790`, but the script can be easily modified to use for other turbines by changing data source and related external ids.
