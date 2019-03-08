#!/usr/bin/python3
activate_this = '/var/www/FlaskApp/FrTvDld/.venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp/FrTvDld/frenchtvdownload")

from app import connex_app as application
application.secret_key = 'Add your secret key'

