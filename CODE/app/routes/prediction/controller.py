import requests
from app import app
from flask import Blueprint, request, render_template
import app.commons.buildResponse as buildResponse
from datetime import datetime, timedelta

prediction = Blueprint('prediction', __name__, url_prefix='/predict')

"""
API for predicting delay for a single flight
Parameters: flight identifier, date, 
Return: Dictionary: {delay: '', factors: [{name:'', value:''}], predictionConfidence: ''}
"""


@prediction.route('/singleFlight', methods=['POST'])
def predictDelay():
    requestJson = request.get_json(silent=True)
    flightId = requestJson["flightId"]
    date = requestJson["date"]
    predictedDict = {}
    result = {}
    if flightId in app.config["FLIGHT_PREDICTION_DATEWISE_DATA_DEPARTURE"][date]:
        predictedDict = app.config["FLIGHT_PREDICTION_DATEWISE_DATA_DEPARTURE"][date][flightId]
        result["ORIGIN"] = "Dubai"
        result["DESTINATION"] = predictedDict["Destination City"]
    elif flightId in app.config["FLIGHT_PREDICTION_DATEWISE_DATA_ARRIVAL"][date]:
        predictedDict = app.config["FLIGHT_PREDICTION_DATEWISE_DATA_ARRIVAL"][date][flightId]
        result["ORIGIN"] =  predictedDict["Origin City"]
        result["DESTINATION"] = "Dubai"
    result["Prediction"] = predictedDict["Prediction"]
    result["MLI"] = predictedDict["MLI"]
    result["Recommendations"] = predictedDict["Recommendations"]
    return buildResponse.buildJson(result)


"""
API for predicting/fetching delays for a single flight over a period of time
Parameters: flight identifier, days, date
Return: List: [{'day':'', delay: ''}]
"""


@prediction.route('/singleFlightSeries', methods=['POST'])
def predictDelaySeries():
    requestJson = request.get_json(silent=True)
    flightId = requestJson["flightId"]
    days = int(requestJson["days"])
    date = requestJson["date"]
    seriesData = []
    if flightId in app.config["FLIGHT_SERIES_DATA_DEPARTURE"]:
        seriesData = app.config["FLIGHT_SERIES_DATA_DEPARTURE"][flightId]
    elif flightId in app.config["FLIGHT_SERIES_DATA_ARRIVAL"]:
        seriesData = app.config["FLIGHT_SERIES_DATA_ARRIVAL"][flightId]
    requestDate = datetime.strptime(date, app.config["DATE_FORMAT"])
    resultArr = []
    for i in range(0, days + 1):
        formattedDate = (requestDate - timedelta(days=days - i)).date().strftime(app.config["DATE_FORMAT"])
        if formattedDate in seriesData:
            resultArr.append({"day": i + 1, "date": formattedDate, "Prediction": seriesData[formattedDate]["Prediction"]})
    # fetch previous delay data/predict in case of future
    return buildResponse.buildJson(resultArr)
