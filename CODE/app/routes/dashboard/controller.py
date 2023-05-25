import requests
from app import app
from flask import Blueprint, request, render_template

dashboard = Blueprint('dashboard', __name__, url_prefix='/', template_folder='templates')


@dashboard.route('/', methods=['GET'])
@dashboard.route('/home', methods=['GET'])
def index():
    return render_template('form.html', baseUrl=app.config["BASE_URL"])


@dashboard.route('/home/prediction', methods=['GET', 'POST'])
def predictionPage():
    return render_template('dashboard.html', baseUrl=app.config["BASE_URL"])
