# -*- coding: utf-8 -*-
"""flight_arrivals_modelling

# Start
Install and Import Packages.
Change runtime to GPU before beginning.
"""

!pip install -q catboost

!pip install -q shap

!pip install -q seaborn

# generic libraries
import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
pd.set_option('display.max_columns', None)

# Stats/ML libraries
from catboost import *
import shap
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, classification_report
from scipy.stats import zscore 

"""# Import Data

Arrivals data can be accessed [here](https://www.dubaipulse.gov.ae/data/dubai-airports-flight-info/da_flight_information_arrivals-open) and weather data can be accessed [here](https://www.ncei.noaa.gov/access/search/data-search/global-summary-of-the-day?stations=41194099999&startDate=2020-01-01T00:00:00&endDate=2023-01-01T23:59:59).

For a description of the weather data, click [here](https://www.ncei.noaa.gov/data/global-summary-of-the-day/doc/readme.txt).
"""

# Load arrivals data from csv
# For this to work, add a shortcut to the shared drive to 'My Drive' (your google drive) and authorize access when the cell above asks for it
# The csv has already been uploaded to the shared folder
arrivals = pd.read_csv("data/Flight_Information_Arrivals.csv")

# Calculate delay from timestamps
arrivals['delay'] = pd.to_timedelta(pd.to_datetime(arrivals['actualInblockTime']) - pd.to_datetime(arrivals['scheduledInblockTime']), unit = 'm')

# Replace the originName column with the viaName column if viaName is not null
# This is because we only consider direct flights
arrivals['originName'] = np.where(arrivals['viaName'].notnull(), arrivals['viaName'], arrivals['originName'])

# Add a date column (extract dates from schedule) for merge with weather data
arrivals['DATE'] = pd.to_datetime(arrivals['publicScheduledDateTime']).dt.date

# Similarly, load weather the weather csvs
w2020 = pd.read_csv("data/weather_data_2020.csv", dtype = {'FRSHTT': str})
w2021 = pd.read_csv("data/weather_data_2021.csv", dtype = {'FRSHTT': str})
w2022 = pd.read_csv("data/weather_data_2022.csv", dtype = {'FRSHTT': str})
w2023 = pd.read_csv("data/weather_data_2023.csv", dtype = {'FRSHTT': str})

# Now concatenate the weather data
weather = pd.concat([w2020, w2021, w2022, w2023])

# Change date datatype from string to date
weather['DATE'] = pd.to_datetime(weather['DATE']).dt.date

# Now merge the arrivals and weather data
data = arrivals.merge(weather, on='DATE', how='left')

"""# Data Cleaning

## Outlier Removal and Bucketing Delays
* Bin delays into 30 minute intervals
* Normalize delays
* Remove all records with delays +/- 3SDs away from the mean
"""

# grab the delay column
# count seconds in the delay
# convert to minutes
# cast to integer
# impute missing values with zeroes

if data['delay'].dtype == '<m8[ns]': # this condition is here to allow us to re-run this cell without bugging the date-time functions
    data['delay'] = data['delay']\
        .dt.total_seconds()\
        .div(60)\
        .astype(int, errors='ignore')\
        .fillna(0)

# Define a function to bin delays into delay intervals
def time_segment(time_min):
    if time_min <= 15: # on time arrivals
        return 0
    elif 15 < time_min  and time_min <= 60: # delay upto 1 hour
        return 1
    else: # delay greater than one hour
        return 2

data['delay_segment'] = data['delay'].apply(lambda x: time_segment(x)) # create new column with binned delays

# use z-scores to standardize delays
data['delayZScore'] = zscore(data['delay'])

# remove all rows with delays over 3 standard deviations away from the mean
data = data[(data['delayZScore'] <= 3) & (data['delayZScore'] >= -3)]

"""## Drop unneccesary columns"""

# Look at what columns we have
data.columns

"""Columns to remove:

* 'aodbUniqueField' - primary key
* 'trafficTypeCode' - same as trafficType
* 'flightStatus', 'flightStatusCode' - not relevant for past data
* 'aircraftRegistration' - not relevant
* 'arrivalOrDeparture' - all flights are arrivals
* 'tenMileOut' - very closely linked to in block time
* 'lastChanged' - operational data, not relevant
* 'airlineCode_iata', 'airlineCode_icao' - same as airline name
* 'via_iata', 'via_icao' - same as via name
* 'viaName' - imputed into originName
* 'origin_iata', 'origin_icao' - same as originName
* 'airlineNameA' - airline name in Arabic
* 'originNameA' - origin name in Arabic
* 'viaNameA' - via name in Arabis
* 'flightStatusTextA' - flight status in Arabic
* 'destination_icao' - same as destination_iata
* 'aircraft_icao' - same as aircraft_iata
* 'scheduledInblockTime', 'actualInblockTime' - these were used to calculate the delay
* 'estimatedInblockTime' - this is an estimate that DXB airport officials make
* 'delayZScore' - information captured in delay
* 'STATION', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'NAME' - these are constant for DXB
* 'SNDP' - doesn't snow in Dubai, not applicable
* 'MXSPD' - max wind speed correlated with mean wind speed and gust
* 'SLP' - mean sea level pressure correlated with mean station pressure as Dubai is at a low elevation
* 'TEMP_ATTRIBUTES', 'DEWP_ATTRIBUTES', 'SLP_ATTRIBUTES', 'STP_ATTRIBUTES', 'VISIB_ATTRIBUTES', 'WDSP_ATTRIBUTES', 'MAX_ATTRIBUTES', 'MIN_ATTRIBUTES', 'PRCP_ATTRIBUTES' - these indicate how the weather data was collected
* 'MAX', 'MIN' - these are the max and min temps on a given day, we will use mean temp only ('TEMP') to avoid correlated features
* 'actualLandingTime' - not useful without estimated landing time
* 'baggageClaimUnit' - bags are loaded after the plane lands and docks, so this shouldn't impact delay
"""

data.drop(columns = ['aodbUniqueField', 'trafficTypeCode', 'flightStatus', 'flightStatusCode', 'actualLandingTime',
                    'aircraftRegistration', 'arrivalOrDeparture', 'tenMileOut', 'lastChanged', 'baggageClaimUnit',
                    'airlineCode_iata', 'airlineCode_icao', 'via_iata', 'via_icao', 'viaName', 'airlineNameA', 
                    'originNameA', 'viaNameA', 'flightStatusTextA', 'destination_icao', 'aircraft_icao', 'delayZScore',
                    'scheduledInblockTime', 'actualInblockTime', 'estimatedInblockTime', 'origin_iata', 'origin_icao', 
                    'STATION', 'LATITUDE', 'LONGITUDE', 'MAX', 'MIN', 'ELEVATION', 'SNDP', 'TEMP_ATTRIBUTES', 'MXSPD',
                    'SLP', 'MAX_ATTRIBUTES', 'MIN_ATTRIBUTES', 'PRCP_ATTRIBUTES', 'DEWP_ATTRIBUTES', 'SLP_ATTRIBUTES',
                    'STP_ATTRIBUTES', 'VISIB_ATTRIBUTES', 'WDSP_ATTRIBUTES', 'NAME'],
          inplace = True)

"""## Handle Missing Data"""

# First we get rid of all the rows with null values in the weather data
data.dropna(axis = 0, subset = ['TEMP', 'DEWP', 'STP', 'VISIB', 'WDSP', 'GUST', 'PRCP', 'FRSHTT'], inplace = True)

# Now we need to replace all 999.9 in the GUST and STP columns with the mode of the respective column
# 999.9 indicates a mising value
modes = {}
for i in ['GUST', 'STP']:
    res = data.loc[data[i] != 999.9, i].mode().values[0]
    modes[i] = res

for k,v in modes.items():
    data.loc[data[k] == 999.9, k] = v

# Also replace the missing parking positions with the most frequently occuring position
modeParking = data.aircraftParkingPosition.mode(dropna = True).values[0]
data.loc[data['aircraftParkingPosition'].isnull(), 'aircraftParkingPosition'] = modeParking

# convert aircraftTerminal to string - this column has mixed string and integer entries
data.loc[:, 'aircraftTerminal'] = data.aircraftTerminal.astype(str)

"""## Feature Engineering



"""

# re-examine what's left
data.columns

sns.heatmap(data.corr(), cmap="PiYG", center = 0.0)
# Doesn't seem like there's much correlation between the delay and any of the numerical features
# But we can see that the weather features are correlated

# The dataset contains records of arrivals at both, DXB and DWC 
# data.destination_iata.value_counts() #uncomment this to check
# Filter it out so that we only include DXB flight data and then drop destination_iata
data = data[data.destination_iata == 'DXB']

# some airlines have a jointFlightnumber
# create an indicator column for this (flight operated by >1 airline), and drop jointFlightNumber
conditions = [data.jointFlightNumber.isnull(),
              data.jointFlightNumber.notnull()]
values = [0,1]
data['Multiple Operators'] = np.select(conditions, values)

# From the publicScheduledDateTime column, extract the month, day_of_month and day_of_week
# Then drop publicScheduledDateTime
data.loc[:, 'Year'] = data['DATE'].apply(lambda x: int(str(x).split("-")[0]))
data.loc[:, 'Month'] = data['DATE'].apply(lambda x: int(str(x).split("-")[1]))
data.loc[:, 'Day Of Month'] = data['DATE'].apply(lambda x: int(str(x).split("-")[2]))
data.loc[:, 'Day Of Week'] = data['DATE'].apply(lambda x: int(x.weekday()))

#Split the FRSHTT column into separate columns for each of the represented weather conditions (for, rain, snow, hail, thunder, tornado)
# Before doing this, we need to impute the NaNs with 0s
data.FRSHTT.fillna('000000', inplace = True)
weather_chars = ['Fog', 'Rain', 'Snow', 'Hail', 'Thunder', 'Tornado']
for i in range(len(weather_chars)):
    data[weather_chars[i]] = data.FRSHTT.apply(lambda x: int(x[i]))

# There are 149 airlines and not all of them have operations at DXB on the same scale
# instead of individually representing each airline, we will only individually represent the airlines that contribute 80% of the flights in our dataset, and group the rest into an 'other' column (pareto principle)
# First, get a list of these airlines, then replace
airlines = data.airlineName.value_counts()
topAirlines = airlines[round(airlines.cumsum()/airlines.sum()*100,2) <= 80].index.tolist()
data.loc[~data['airlineName'].isin(topAirlines), 'airlineName'] = 'Other'

# same thing for flight numbers
flights = data.flightNumber.value_counts()
top_flights = flights[round(flights.cumsum()/flights.sum()*100,2) <= 80].index.tolist()
data.loc[~data['flightNumber'].isin(top_flights), 'flightNumber'] = 'Other'

# Now drop destination_iata, jointFlightNumber, publicScheduledDateTime, FRSHTT
data.drop(columns = ['destination_iata', 'jointFlightNumber', 'publicScheduledDateTime', 'FRSHTT', 'Snow', 'Tornado'], inplace = True)

# finally, examine remaining columns again
data.columns

"""## Rename Columns"""

data.rename(columns = {'flightNumber':'Flight Number', 
                       'aircraft_iata': 'Aircraft Type',
                       'aircraftParkingPosition': 'Parking Position',
                       'airlineName': 'Airline', 
                       'originName': 'Origin City', 
                       'trafficType': 'Traffic Type', 
                       'aircraftTerminal': 'Terminal', 
                       'delay': 'Delay',
                       'DATE': 'Date', 
                       'TEMP': 'Mean Temperature', 
                       'DEWP': 'Dewpoint', 
                       'STP': 'Station Pressure', 
                       'VISIB': 'Visibility', 
                       'WDSP': 'Windspeed', 
                       'GUST': 'Maximum Gust', 
                       'PRCP': 'Precipitation',
                       'delay_segment': 'Delay Segment'}, inplace = True)

"""# Train Delay Prediction Model

We will split the data into training and test samples.
The first 80% of the data (by date) will be used for training and the last 20% (most recent) data will be used for testing.

## Split Training and Testing Data
"""

threshold_date = pd.to_datetime("2022-10-01", format='%Y-%m-%d')

train = data[data.Date <= threshold_date]
test = data[data.Date > threshold_date]

X_train = train.drop(columns = ['Delay', 'Delay Segment', 'Date'])
X_test = test.drop(columns = ['Delay', 'Delay Segment', 'Date'])

y_train = train['Delay Segment']
y_test = test['Delay Segment']

"""## Train and Evaluate Catboost Model"""

model = CatBoostClassifier(task_type='GPU', devices='0')
model.fit(X_train, y_train, cat_features = ['Flight Number', 'Aircraft Type', 'Parking Position', 'Airline', 'Origin City', 'Traffic Type', 'Terminal'], logging_level = 'Silent')

# Make predictions using the fitted model and print performance results/
y_preds = model.predict(X_test)
print(classification_report(y_test, y_preds))

"""# Feature Importance

## Model-level Feature Importance
"""

importance = pd.DataFrame({'columns': X_train.columns, 'importance': model.feature_importances_})
top_10_features = importance.sort_values('importance', ascending=False).head(10).reset_index().drop(columns = ['index'])
top_10_sum = np.sum(np.sum(top_10_features['importance']))
print(f'These features represent {round(top_10_sum,2)}% of the variability in the data:')
display(top_10_features)

"""## Local Feature Importance"""

explainer = shap.Explainer(model)
importances = explainer.shap_values(X_test[:10])

local_xai = pd.DataFrame({'feature_names': X_test.columns, 'feature_value': list(X_test.iloc[0]), 'feature_importances': importances[1][0]})
local_xai['sign'] = local_xai['feature_importances'].apply(lambda x: np.sign(x))
local_xai['feature_importances'] = local_xai['feature_importances'].apply(lambda x: np.abs(x))
local_xai = local_xai.sort_values(by=['feature_importances'], ascending=False)
local_xai['feature_importances'] = local_xai['feature_importances'] * local_xai['sign']
local_xai = local_xai.drop(columns=['sign'])
local_xai.head(5).to_dict('records')

importances = explainer.shap_values(X_test)
mli = []
for i in range(len(X_test)):
  local_xai = pd.DataFrame({'feature_names': X_test.columns, 'feature_value': list(X_test.iloc[i]), 'feature_importances': importances[1][i]})
  local_xai['sign'] = local_xai['feature_importances'].apply(lambda x: np.sign(x))
  local_xai['feature_importances'] = local_xai['feature_importances'].apply(lambda x: np.abs(x))
  local_xai = local_xai.sort_values(by=['feature_importances'], ascending=False)
  local_xai['feature_importances'] = local_xai['feature_importances'] * local_xai['sign']
  local_xai = local_xai.drop(columns=['sign'])
  mli.append(local_xai.head(5).to_dict('records'))
X_test.loc[:, "MLI"] = mli

output = pd.DataFrame(X_test)
output.loc[:, "Prediction"] = y_preds
output.head()

"""# Similar Flights
We will use the output of the delay prediction (CatBoost) and the feature importance results to recommend similar flights to the selected flight.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# 
# # Re-create a date column from the year month and day columns
# output.loc[:, "Date"] = output.apply(lambda x: pd.to_datetime(f'{x["Year"]}-{x["Month"]}-{x["Day Of Month"]}'), axis=1)
# 
# recs = []
# for i in range(len(output)):
#     # Select a point from the data
#     test_point = output.iloc[i]
#     # We will only recommend similar flights if they're within a 5 day range from the selected date of travel
#     date_range = [str(test_point.Date - datetime.timedelta(days=j)) for j in range(-5,5)]
#     # Now we will extract all the flights that match the origin port of the selected flight, and have a delay prediction of 0, ie, not delayed
#     candidates = output.loc[(output['Prediction'] == 0) & (output['Origin City'] == test_point['Origin City']) & (output.Date.isin(date_range)), :]
#     candidates.loc[:,'Date'] = candidates.Date.dt.strftime("%Y-%m-%d")
#     similarFlights = candidates[:5][['Flight Number', 'Airline', 'Origin City', 'Date']].to_dict('record')
#     recs.append(similarFlights)
# output.loc[:, 'Recommendations'] = recs

"""# Export"""

# Change delay segments to readable categories
output.loc[output['Prediction'] == 0, 'Prediction'] = 'No Delay Predicted'
output.loc[output['Prediction'] == 1, 'Prediction'] = 'Delay Upto 1 Hour Predicted'
output.loc[output['Prediction'] == 2, 'Prediction'] = 'Delay >1 Hour Predicted'

# examine final output
output.head()

# export csv to google drive
path = '/content/gdrive/MyDrive/CSE6242/results/arrival_prediction_outputs.csv'
with open(path, 'w', encoding = 'utf-8-sig') as f:
  output.to_csv(f)