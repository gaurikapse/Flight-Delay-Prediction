import requests
from app import app
from flask import Blueprint, request, render_template
import app.commons.buildResponse as buildResponse

weather = Blueprint('weather', __name__, url_prefix='/weather')

"""
API for getting weather data for a day
Parameters: date
Return: Dictionary containing weather data
"""
@weather.route('/getWeather', methods=['GET'])
def getWeather():
    requestJson = request.get_json(silent=True)
    #date = requestJson["date"]
    result = {"WindSpeed": "45 km/h", "Humidity":"60%", "Temperature": "30C"}
    return buildResponse.buildJson(result)