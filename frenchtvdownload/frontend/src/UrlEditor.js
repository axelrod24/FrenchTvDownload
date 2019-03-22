import React, { Component } from 'react';

class UrlEditor extends Component {
  constructor(props) {
      super(props)

      this.onChange = this.onChange.bind(this)

      this.state = {
          addUrlButtonEnable : false
      }
  }

  render() {
      return (
          <div className="editor">
              <label htmlFor="url" style={{width: '80%'}}>Url :
                  <input id="url" ref="_url" type="text" style={{width: '80%'}} onChange={evt => this.onChange(evt)}/>
                  <button disabled={!this.state.addUrlButtonEnable} onClick={()=> this.props.onAddUrl(this.refs._url.value)}>Add Url</button>
              </label>
          </div>
      )
  }

  onChange(evt) {
      if (this._isURL(evt.target.value)) {
          if (!this.state.addUrlButtonEnable)
          {
              this.setState({
                  addUrlButtonEnable : true
              })
          }
      }
      else {
          if (this.state.addUrlButtonEnable)
          {
              this.setState({
                  addUrlButtonEnable : false
              })
          }
      }
  }

  _isURL(str) {
      var pattern = new RegExp('^((ft|htt)ps?:\\/\\/)?'+ // protocol
      '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name and extension
      '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
      '(\\:\\d+)?'+ // port
      '(\\/[-a-z\\d%@_.~+&:]*)*'+ // path
      '(\\?[;&a-z\\d%@_.,~+&:=-]*)?'+ // query string
      '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
      return pattern.test(str);
    }    
}

export default UrlEditor
