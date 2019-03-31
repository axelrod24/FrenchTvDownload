
const URL_BASE = "http://localhost:5000/"
const URL_PATH = "api/video"

class WebApi {
  constructor(callback) {
    this.callback = callback

    this._fetch = this._fetch.bind(this)
  }

  getVideoList() {
    var url = URL_BASE + URL_PATH
    this._fetch(url)
  }

  getVideoById(video_id) {
    var url = URL_BASE + URL_PATH + "?id="+video_id
    this._fetch(url)
  }

  addVideoUrl(video_url) {
    var url = URL_BASE + URL_PATH + "?url="+video_url
    this._fetch(url, {method: "POST"})
  }

  removeVideoById(video_id) {
    var url = URL_BASE + URL_PATH + "/delete?id="+video_id
    this._fetch(url)
  }

  downloadVideoById(video_id) {
    var url = URL_BASE + URL_PATH + "/download?id="+video_id
    this._fetch(url)
  }

  cancelDownloadById(video_id) {
    var url = URL_BASE + URL_PATH + "/cancel?id="+video_id
    this._fetch(url)
  }
  
  getDownloadStatusById(video_id) {
    var url = URL_BASE + URL_PATH + "/status?id="+video_id
    this._fetch(url)
  }
  _handleErrors(response) {
    if (!response.ok) {
        throw Error(response.status+" "+response.statusText);
    }
    return response;
  }

  _fetch(url, method = {}) {
    fetch(url, method).then(this._handleErrors).then(res => res.json()).then(this.callback).catch(error => console.log('Request failed', error))
    console.log("Fetching:", url)
  }
}

export default WebApi