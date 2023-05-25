import datetime
import urllib.parse
import csv
import json
import ast
import pandas as pd


def loadPredictedDataDeparture(DATE_FORMAT, BASE_URL):
    df = pd.read_csv('app/static/departure_prediction_outputs.csv')
    predictedData = {}
    flights = {}
    flightSeriesData = {}
    for i in range(0, len(df)):
        date = datetime.date(year=df["Year"][i], month=df["Month"][i], day=df["Day Of Month"][i])
        formatted_date = date.strftime(DATE_FORMAT)
        flights[df["Flight Number"][i]] = []
        if formatted_date not in predictedData:
            predictedData[formatted_date] = {}
        lineData = {"Parking Position": df["Parking Position"][i], "Aircraft Type": df["Aircraft Type"][i],
                    "Airline": df["Airline"][i], "Destination City": df["Destination City"][i],
                    "Terminal": df["Terminal"][i], "Traffic Type": df["Traffic Type"][i],
                    "Mean Temperature": df["Mean Temperature"][i], "Dewpoint": df["Dewpoint"][i],
                    "Station Pressure": df["Station Pressure"][i], "Visibility": df["Visibility"][i],
                    "Windspeed": df["Windspeed"][i], "Maximum Gust": df["Maximum Gust"][i],
                    "Precipitation": df["Precipitation"][i],
                    "Multiple Operators": df["Multiple Operators"][i], "MONTH": df["Month"][i], "YEAR": df["Year"][i],
                    "Day Of Month": df["Day Of Month"][i], "Day Of Week": df["Day Of Week"][i], "Fog": df["Fog"][i],
                    "Rain": df["Rain"][i], "Hail": df["Hail"][i], "Thunder": df["Thunder"][i],
                    "MLI": ast.literal_eval(df["MLI"][i]),
                    "Prediction": df["Prediction"][i], "Recommendations": ast.literal_eval(df["Recommendations"][i]),
                    "date": formatted_date
                    }
        for j in range(0, len(lineData["Recommendations"])):
            lineData["Recommendations"][j]["url"] = BASE_URL + "/home/prediction?flight=" + urllib.parse.quote_plus(
                lineData["Recommendations"][j]["Flight Number"]) + "&date=" + lineData["Recommendations"][j]["Date"]
        predictedData[formatted_date][df["Flight Number"][i]] = lineData

        if df["Flight Number"][i] not in flightSeriesData:
            flightSeriesData[df["Flight Number"][i]] = {}
        flightSeriesData[df["Flight Number"][i]][formatted_date] = {"Prediction": df["Prediction"][i],
                                                                    "MLI": ast.literal_eval(df["MLI"][i]), "date": date}
    return predictedData, list(flights.keys()), flightSeriesData


def loadPredictedDataArrival(DATE_FORMAT, BASE_URL):
    df = pd.read_csv('app/static/arrival_prediction_outputs.csv')
    predictedData = {}
    flights = {}
    flightSeriesData = {}
    for i in range(0, len(df)):
        date = datetime.date(year=df["Year"][i], month=df["Month"][i], day=df["Day Of Month"][i])
        formatted_date = date.strftime(DATE_FORMAT)
        flights[df["Flight Number"][i]] = []
        if formatted_date not in predictedData:
            predictedData[formatted_date] = {}
        lineData = {"Parking Position": df["Parking Position"][i], "Aircraft Type": df["Aircraft Type"][i],
                    "Airline": df["Airline"][i], "Origin City": df["Origin City"][i],
                    "Terminal": df["Terminal"][i], "Traffic Type": df["Traffic Type"][i],
                    "Mean Temperature": df["Mean Temperature"][i], "Dewpoint": df["Dewpoint"][i],
                    "Station Pressure": df["Station Pressure"][i], "Visibility": df["Visibility"][i],
                    "Windspeed": df["Windspeed"][i], "Maximum Gust": df["Maximum Gust"][i],
                    "Precipitation": df["Precipitation"][i],
                    "Multiple Operators": df["Multiple Operators"][i], "MONTH": df["Month"][i], "YEAR": df["Year"][i],
                    "Day Of Month": df["Day Of Month"][i], "Day Of Week": df["Day Of Week"][i], "Fog": df["Fog"][i],
                    "Rain": df["Rain"][i], "Hail": df["Hail"][i], "Thunder": df["Thunder"][i],
                    "MLI": ast.literal_eval(df["MLI"][i]),
                    "Prediction": df["Prediction"][i], "Recommendations": ast.literal_eval(df["Recommendations"][i]),
                    "date": formatted_date
                    }
        for j in range(0, len(lineData["Recommendations"])):
            lineData["Recommendations"][j]["url"] = BASE_URL + "/home/prediction?flight=" + urllib.parse.quote_plus(
                lineData["Recommendations"][j]["Flight Number"]) + "&date=" + lineData["Recommendations"][j]["Date"]
        predictedData[formatted_date][df["Flight Number"][i]] = lineData

        if df["Flight Number"][i] not in flightSeriesData:
            flightSeriesData[df["Flight Number"][i]] = {}
        flightSeriesData[df["Flight Number"][i]][formatted_date] = {"Prediction": df["Prediction"][i],
                                                                    "MLI": ast.literal_eval(df["MLI"][i]), "date": date}
    return predictedData, list(flights.keys()), flightSeriesData


class Config():
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True
    TEMPLATES_AUTO_RELOAD = True
    BASE_URL = "http://127.0.0.1:5433"
    DATE_FORMAT = "%Y-%m-%d"
    FLIGHT_PREDICTION_DATEWISE_DATA_DEPARTURE, ALL_FLIGHTS_DEPARTURE, FLIGHT_SERIES_DATA_DEPARTURE = loadPredictedDataDeparture(
        DATE_FORMAT, BASE_URL)
    FLIGHT_PREDICTION_DATEWISE_DATA_ARRIVAL, ALL_FLIGHTS_ARRIVAL, FLIGHT_SERIES_DATA_ARRIVAL = loadPredictedDataArrival(
        DATE_FORMAT, BASE_URL)
