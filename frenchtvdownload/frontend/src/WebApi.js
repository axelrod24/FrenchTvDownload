
const URL_BASE = "http://localhost:5000/"
const URL_PATH = "api/video"

class WebApi {
  constructor(callback, error) {
    this.callback = callback
    this.error = error 

    this._handleNetworkErrors = this._handleNetworkErrors.bind(this)
    this._processResponse = this._processResponse.bind(this)
    this._fetch = this._fetch.bind(this)
  }

  getVideoList() {
    this.url = URL_BASE + URL_PATH
    this._fetch(this.url)
  }

  getVideoById(video_id) {
    this.url = URL_BASE + URL_PATH + "?id="+video_id
    this._fetch(this.url)
  }

  addVideoUrl(video_url) {
    this.url = URL_BASE + URL_PATH + "?url="+video_url
    this._fetch(this.url, {method: "POST"})
  }

  removeVideoById(video_id) {
    this.url = URL_BASE + URL_PATH + "/delete?id="+video_id
    this._fetch(this.url)
  }

  downloadVideoById(video_id) {
    this.url = URL_BASE + URL_PATH + "/download?id="+video_id
    this._fetch(this.url)
  }

  cancelDownloadById(video_id) {
    this.url = URL_BASE + URL_PATH + "/cancel?id="+video_id
    this._fetch(this.url)
  }
  
  getDownloadStatusById(video_id) {
    this.url = URL_BASE + URL_PATH + "/status?id="+video_id
    this._fetch(this.url)
  }

  _handleNetworkErrors(response) {
    if (!response.ok) {
        throw Error(response.status+" "+response.statusText);
    }
    return response;
  }

  _processResponse(resp) {
    if (!resp.status) {
      var str = "Error fetching: "+ this.url 
      str += "\nNo status field for:"+ resp
      console.log(str)
      if (this.error)
        this.error(resp)
    }

    (resp.status === "error") ? ((this.error) ? this.error(resp.data) : console.log("Error: "+resp.data)) : this.callback(resp.data)
  }

  _fetch(url, method = {}) {
    fetch(url, method).then(this._handleNetworkErrors).then(res => res.json()).then(this._processResponse).catch(error => console.log('Request failed', error))
    console.log("Fetching:", url)
  }
}

export default WebApi
