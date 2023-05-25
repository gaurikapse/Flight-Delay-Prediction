from flask import Flask
import app.config

app = Flask(__name__)

#development server config
app.config.from_object('app.config.Config')

@app.errorhandler(404)
def not_found(error):
    return "Not found", 404

from app.routes.dashboard.controller import dashboard as dashboard
from app.routes.prediction.controller import prediction as prediction
from app.routes.weather.controller import weather as weather
from app.routes.flights.controller import flight as flight

app.register_blueprint(dashboard)
app.register_blueprint(prediction)
app.register_blueprint(weather)
app.register_blueprint(flight)
