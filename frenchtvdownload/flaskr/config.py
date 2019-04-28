import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(basedir, 'people.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["DLD_THREAD"] = dict() # hashmap to store active download thread
app.config["PIPE_NAME_HEADER"] = "fifo-%s-dld"

if app.config["ENV"] == 'production':
    app.config["DST_FOLDER"] = os.path.join("/home", "lbr", "Dropbox", "FRTV_DLD_FOLDER")
    app.config["TMP_FOLDER"] = os.path.join("/var", "www", "FlaskApp", "FrTvDld",  "TMP_FRTV_DLD_FOLDER")
else:
    app.config["DST_FOLDER"] = os.path.join(basedir, "FRTV_DLD_FOLDER")
    app.config["TMP_FOLDER"] = os.path.join(basedir, "FRTV_TMP_FOLDER")

# create the working folder
if not os.path.exists(app.config["DST_FOLDER"]):
    os.mkdir(app.config["DST_FOLDER"])

if not os.path.exists(app.config["TMP_FOLDER"]):
    os.mkdir(app.config["TMP_FOLDER"])

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

