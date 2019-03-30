import sys, os
import logging
from flask import render_template, jsonify, make_response, abort

# local modules
from flaskr import config
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

template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "frontend", "build" )
static_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "frontend", "build", "static")


# Create the application instance
app = config.app
app.template_folder = template_dir
app.static_folder = static_dir
app.static_url_path = "/static"

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/video', methods=['GET'])
def read_all_video():
    print("read_all_video")
    return jsonify(flaskr.video.read_all())


@app.route('/api/video/<string:video_id>', methods=['GET'])
def read_one_video(video_id):
    print("read_one_video:", video_id)
    return jsonify(flaskr.video.read_one(video_id))


@app.route('/api/download/<string:video_id>', methods=['GET'])
def download_video(video_id):
    print("Download video:", video_id)
    video = flaskr.video.download(video_id)
    if video is None:
        abort(404)

    return jsonify(video)


@app.route('/api/cancel/<string:video_id>', methods=['POST'])
def cancel_download_video(video_id):
    print("cancel_download_video:", video_id)
    return jsonify(flaskr.video.cancel(video_id))


@app.route('/api/status/<string:video_id>', methods=['GET'])
def get_download_status(video_id):
    print("get_download_status:", video_id)
    return jsonify(flaskr.video.get_status(video_id))


    
# # Create a URL route in our application for "/"
# @connex_app.route('/')
# def home():
#     """
#     This function just responds to the browser ULR
#     localhost:5000/
#     :return:        the rendered template 'home.html'
#     """
#     # return render_template('home.html')
#     return render_template('index.html')

# If we're running in stand alone mode, run the application
# if __name__ == '__main__':
#     template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "frontend", "build" )
#     static_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "frontend", "build", "static")
#     # connex_app.app.template_folder = template_dir
#     # connex_app.app.static_folder = static_dir
#     # connex_app.app.static_url_path = "/static"
#     # if connex_app.app.config["ENV"] == 'production':
#     #     connex_app.run(debug=True)
#     # else:
#     #     connex_app.run(host='0.0.0.0', port=5000, debug=True)

#     connex_app.template_folder = template_dir
#     connex_app.static_folder = static_dir
#     connex_app.static_url_path = "/static"
#     print("in the main")
#     if connex_app.config["ENV"] == 'production':
#         connex_app.run(debug=True)
#     else:
#         connex_app.run(host='0.0.0.0', port=5000, debug=True)


