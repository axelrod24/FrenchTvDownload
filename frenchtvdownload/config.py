import os
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

basedir = os.path.abspath(os.path.dirname(__file__))

# Create the Connexion application instance
connex_app = connexion.App(__name__, specification_dir=basedir)

# Get the underlying Flask app instance
app = connex_app.app

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(basedir, 'people.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["DLD_THREAD"] = dict() # hashmap to store active download thread
app.config["PIPE_NAME_HEADER"] = "fifo-%s-dld"
app.config["DLD_FOLDER"] = "FRTV_DLD_FOLDER"

if not os.path.exists(app.config["DLD_FOLDER"]):
    os.mkdir(app.config["DLD_FOLDER"])

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Initialize Marshmallow
ma = Marshmallow(app)

