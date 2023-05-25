DESCRIPTION
------------
The web application uses Flask for backend and HTML, CSS, and JavaScript for the frontend. Bootstrap is used for the CSS styling, and the interactive charts are built using D3.js. The web application fetches the data from pre-computed batch predictions and displays the delay prediction along with recommendations and interactive visualizations for the selected flight on a dashboard. 

INSTALLATION
-------------
Python: 3.8

1. Download the project.

2. Unzip the zip file using any zip software.

3. Open a terminal and navigate to the directory of the unzipped folder. 	E.g. ./CODE

4. Install the requirements using the following command- 
   `pip3 install -r requirements.txt`

EXECUTION
----------
1. Server can be started locally (in the project 'CODE' directory: ./CODE/) using the command- 
    `python3 run.py`

* In case the above command doesn't work for you, you can try the same command without specifying the python version-
    `python run.py`

2. Navigate to `http://127.0.0.1:5433/` or `localhost:5433/`

3. Input flight number and date in form fields.

Sample flights for testing: 
  Flight Number     Date
- 6H 661            2022-10-21
- AH 4062           2022-10-21
- IX 191            2022-10-20

NOTE: CSV files containing prediction outputs for arriving and departing flights can be found in CODE/app/static/

DEMO VIDEO
----------
Please follow this link for the Demo Video : https://youtu.be/DiDkDBAxnhc

DATA
----------
Raw data can be downloaded from the following links:
- flight departures: https://www.dubaipulse.gov.ae/data/dubai-airports-flight-info/da_flight_information_departures-open
- flight arrivals: https://www.dubaipulse.gov.ae/data/dubai-airports-flight-info/da_flight_information_arrivals-open
- weather: https://www.ncei.noaa.gov/access/search/data-search/global-summary-of-the-day




