import sys
import logging
from flask import render_template

# local modules
import config
from frtvdld.GlobalRef import LOGGER_NAME
from frtvdld.ColorFormatter import ColorFormatter

# set logger
logger = logging.getLogger(LOGGER_NAME)
console = logging.StreamHandler(sys.stdout)
# if (args.verbose):
#     logger.setLevel(logging.DEBUG)
#     console.setLevel(logging.DEBUG)
# else:
#     logger.setLevel(logging.INFO)
#     console.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
console.setLevel(logging.DEBUG)
console.setFormatter(ColorFormatter(False))  # no color
logger.addHandler(console)

# Create the application instance
connex_app = config.connex_app

# Read the swagger.yml file to configure the endpoints
connex_app.add_api('swagger.yml')

# Create a URL route in our application for "/"
@connex_app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    if app.config["ENV"] == 'production':
        connex_app.run(debug=True)
    else:
        connex_app.run(host='0.0.0.0', port=5000, debug=True)



