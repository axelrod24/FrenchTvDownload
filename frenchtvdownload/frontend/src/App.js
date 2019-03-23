import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import UrlTable from './UrlTable.js';
import UrlEditor from './UrlEditor.js';
import {UrlModel, VideoMetaData} from "./model.js"

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: true,
      data: []
    }

    this.onAddUrl = this.onAddUrl.bind(this)
  }

  componentDidMount()
  {
    // fetch original table data
    var url = "http://localhost:5000/api/video"
    fetch(url)
      .then(res => res.json())
      .then(data => {
          var table = []
          data.map(url => table.push(UrlModel(url.video_id, url.url, url.status, url.timestamp, VideoMetaData())))
          this.setState({loading: false, data: table})
        }
      )
      .catch(error => console.log('Request failed', error))  
  }

  componentDidUpdate(prevProps, prevState)
  {
    const { _urleditor, _urltable } = this.refs
    this.urlEditor = _urleditor
    this.urlTable = _urltable
  }

  render() {
    return (
      <div className="container">
        <h1 className="banner">FrenchTV Download List of Url</h1>
        <UrlEditor ref="_urleditor" onAddUrl={this.onAddUrl}/>
        {(this.state.loading) ? <p> loading table</p> : <UrlTable ref="_urltable" data={this.state.data}/>}
      </div>
    );
  }

  onAddUrl(url) {
    this.urlTable.addUrl(url)
  }
}

export default App;
