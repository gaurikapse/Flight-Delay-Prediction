from flask import Blueprint, request

import app.commons.buildResponse as buildResponse
from app import app

flight = Blueprint('flights', __name__, url_prefix='/flight')

"""
API for getting flights along a given time
Parameters: flight identifier, date
Return: List of flights along with their delay predictions
"""


@flight.route('/allFlights', methods=['POST'])
def getAllFlights():
    requestJson = request.get_json(silent=True)
    flightId = requestJson["flightId"]
    date = requestJson["date"]
    print(flightId, date)
    result = []
    return buildResponse.buildJson(result)


"""
API for checking if a flight exists
Parameters: flight identifier, date
Return: Json with true/false
"""


@flight.route('/checkFlight', methods=['POST'])
def checkFlightExists():
    requestJson = request.get_json(silent=True)
    flightId = requestJson["flightId"]
    date = requestJson["date"]
    if (date in app.config["FLIGHT_PREDICTION_DATEWISE_DATA_DEPARTURE"] and flightId in
        app.config["FLIGHT_PREDICTION_DATEWISE_DATA_DEPARTURE"][date]) or (date in
                                                                           app.config[
                                                                               "FLIGHT_PREDICTION_DATEWISE_DATA_ARRIVAL"] and flightId in \
                                                                           app.config[
                                                                               "FLIGHT_PREDICTION_DATEWISE_DATA_ARRIVAL"][
                                                                               date]):
        result = {"flightExists": True}
    else:
        result = {"flightExists": False}
    return buildResponse.buildJson(result)
