import os
import queue

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

PROJECT_BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
PROD_DEPLOY_BASE_PATH = os.path.join("/var", "www", "FlaskApp", "FrTvDld")
DEV_DEPLOY_BASE_PATH = PROJECT_BASE_DIR
DB_FILENAME = "videos.db"

app = Flask(__name__)
CORS(app)

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_ECHO'] = True
if app.config["ENV"] == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(PROD_DEPLOY_BASE_PATH, DB_FILENAME)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(DEV_DEPLOY_BASE_PATH, DB_FILENAME)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["DLD_THREAD"] = dict() # hashmap to store active download thread
app.config["PIPE_NAME_HEADER"] = "fifo-%s-dld"
app.config["QUEUE"] = queue.Queue()

if app.config["ENV"] == 'production':
    app.config["DST_FOLDER"] = os.path.join("/home", "lbr", "Dropbox", "FRTV_DLD_FOLDER")
    app.config["TMP_FOLDER"] = os.path.join("/media", "hd1", "TMP_FRTV_DLD_FOLDER")
else:
    app.config["DST_FOLDER"] = os.path.join(DEV_DEPLOY_BASE_PATH, "FRTV_DLD_FOLDER")
    app.config["TMP_FOLDER"] = os.path.join(DEV_DEPLOY_BASE_PATH, "FRTV_TMP_FOLDER")

# create the working folder
if not os.path.exists(app.config["DST_FOLDER"]):
    os.mkdir(app.config["DST_FOLDER"])

if not os.path.exists(app.config["TMP_FOLDER"]):
    os.mkdir(app.config["TMP_FOLDER"])

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

