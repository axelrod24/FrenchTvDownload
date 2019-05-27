import sys, os
import logging
import flask
from flask import render_template, jsonify, make_response, abort

# local modules
from flaskr import config, models
from flaskr.models import video
from frtvdld.GlobalRef import LOGGER_NAME
from frtvdld.ColorFormatter import ColorFormatter

import flaskr.video

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

logger.info("------------------------------------")
logger.info("--  Start Web App Initialization  --")
logger.info("------------------------------------")

# Create the application instance
app = config.app

if app.config["ENV"] == 'production':
    template_dir = os.path.join(config.PROD_DEPLOY_BASE_PATH, "frontend", "build")
    static_dir = os.path.join(config.PROD_DEPLOY_BASE_PATH, "frontend", "build", "static")

else:
    template_dir = os.path.join(config.DEV_DEPLOY_BASE_PATH, "frontend", "build" )
    static_dir = os.path.join(config.DEV_DEPLOY_BASE_PATH, "frontend", "build", "static")

app.template_folder = template_dir
app.static_folder = static_dir
app.static_url_path = "/static"

# create the DB with table if doesn't exist
if not os.path.exists(app.config['SQLALCHEMY_DATABASE_URI']):
    config.db.create_all()
# clean up downloading status, replace by pending
models.video.clean_model_at_startup()

logger.info("--------------------------------------")
logger.info("-- Web App Initialization completed --")
logger.info("--------------------------------------")

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(409)
def duplicate(error):
    return make_response(jsonify({'error': 'duplicate'}), 409)

# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
    return render_template('index.html')


@app.route('/api/video', methods=['GET', 'POST'])
def get_post_video():
    r = flask.request

    # read list of all video 
    if r.method == 'GET':

        # check for a video_id
        video_id = r.args.get("id", "")
        if len(video_id) == 0:
            return response(flaskr.video.read_all())
        
        # read a specific video_id
        video = flaskr.video.read_one(video_id)
        if video is None:
            return error('Video Id not found:%s'%(video_id))

        return response(video)

    # add a video url
    if r.method == 'POST':
        video_url = r.args.get("url", "")
        if len(video_url) == 0:
            return error('wrong post url')
        
        video = flaskr.video.add_url(video_url)
        if video is None:
            return error('duplicate')

        return response(video)


@app.route('/api/video/download', methods=['GET'])
def download_video():
    # check for a video_id
    r = flask.request
    video_id = r.args.get("id", "")
    if len(video_id) == 0:
        return error('Wrong request')

    video = flaskr.video.download(video_id)
    if video is None:
        return error('Video Id not found:%s'%(video_id))

    return response(video)

    
@app.route('/api/video/delete', methods=['GET'])
def remove_video():
    r = flask.request
    video_id = r.args.get("id", "")
    if len(video_id) == 0:
        return error('Wrong request')

    resp = flaskr.video.delete(video_id)
    if resp is None:
        return error("Can't remove Video id:%s"%(video_id))

    return response({'status': 'success', 'message':"Video %s successfuly removed" % (video_id)})


@app.route('/api/video/cancel', methods=['GET'])
def cancel_download_video():
    r = flask.request
    video_id = r.args.get("id", "")
    if len(video_id) == 0:
        return error('Wrong request')

    print("cancel_download_video:", video_id)
    resp = flaskr.video.cancel(video_id)
    if resp is not True:
        return error("Error cancel download Video id:%s"%(video_id))

    return response(None)


@app.route('/api/video/status', methods=['GET'])
def get_download_status():
    r = flask.request
    video_id = r.args.get("id", "")
    if len(video_id) == 0:
        return error('Wrong request')

    print("get_download_status:", video_id)
    status = flaskr.video.get_status(video_id)
    if status is None:
        return error("Can't read status for Video id:%s"%(video_id))

    return response(status)


def response(resp):
    return jsonify({"status":"success", "data": resp})

def error(resp):
    return jsonify({"status":"error", "data": resp})
