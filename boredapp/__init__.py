import json

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy#
from boredapp.config import DATABASEPASSWORD, DATABASENAME, SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = f"{SECRET_KEY}"  # secret key for the WTForm forms you create
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:{PASSWORD}@localhost/{DatabaseName}'.format(
    PASSWORD=DATABASEPASSWORD, DatabaseName=DATABASENAME)
database = SQLAlchemy(app)


def connect_to_api(url):
    response = requests.get(url)
    dataResponse = response.text
    connection = json.loads(
        dataResponse)  # deserializing - turns json string into python dictionary that can be now accessed

    return connection



from boredapp import routes
