# France_La_Haute_Borne
## France_to_Raw.py
This was used to ingest the Engie data into Raw.

## live_feed_french_turbine_timeseries.py
This requires “data” as an input. And that data should be a dictionary of just one key-value pair. The key needs to be “external_ids” and the values would be a list of the external ids of the Time Series wanted. The defined data external ids are found by pulling in all Time Series with a root asset id for the France_La_Haute_Borne asset. 

This pulls in all Data Points for the Time Series defined by the “data” input. The data points were pulled only for the calculated approximate time frame of between 1 year and 5 days ago to 1 year plus 5 days ago. The Time Stamp for each Data Point is shifted forward 1 year so that it reflects the range from five days ago to five days from now. Then only the data points that are within approximately the last 10 minutes is ingested into CDF.

All time frames were calculated using formulas - this is not the best way to do this, as this doesn’t necessarily give correct time differences or calculations. Since this is not real live data, it’s ok for these purposes (if any concern, please raise issue)

## live_feed_performance_timeseries_french_turbine.py
This requires “data” as an input. And that data should be a dictionary of just one key-value pair. The key needs to be “external_ids” and the values would be a list of the external ids of the Time Series wanted. Four different functions are deployed using this function, just each uses different data. The defined data external ids are all formatted as “France:Performance_[turbine_id]”. 

This pulls in all Data Points for the Time Series defined by the “data” input. The data points were pulled only for the calculated approximate time frame of between 1 year and 5 days ago to 1 year plus 5 days ago. The Time Stamp for each Data Point is shifted forward 1 year so that it reflects the range from five days ago to five days from now. Then only the data points that are within approximately the last 10 minutes is ingested into CDF.

All time frames were calculated using formulas - this is not the best way to do this, as this doesn’t necessarily give correct time differences or calculations. Since this is not real live data, it’s ok for these purposes (if any concern, please raise issue)

## livefeed_sitelevel_weather_timeseries.py
This function works by first checking that the client for cdf is logged in. Then, it makes sure all variables that are required exist in the given data input. It then grabs data from Stormglass using the API. The API call is defined using the inputted API key, the inputted longitude and latitude, the inputted variables, and a start and end time of approximately one day ago and three days from now respectively. If the API call fails, the function errors out. Otherwise, it returns data in a json format. It then loops through each turbine number to do the following for each:

An empty dataframe is created with specifications that will fit the returned json data - it’s done this way to allocate for memory. The data is looped through and filled into the empty dataframe. It then uses a formula to change the timestamp to epoch unix in milliseconds. Then to format the dataframe for the sdk, it makes the timestamp the index of the dataframe, converts column names to external id and then to id of the timeseries it will write to. Lastly, it tries to write the dataframe to cdf 3 times and it will say whether it was successful or not.

The start and end time inputted and the conversion of to epoch unix in milliseconds were calculated using formulas - this is not the best way to do this, as this doesn’t necessarily give correct time differences or calculations. Since this pulls in data for 4 days worth but runs every hour, data overlaps and so it’s ok for these purposes (if any concern, please raise issue)