import React, { Component } from 'react'
import logo from './logo.svg'
import './App.css'
import UrlTable from './UrlTable.js'
import UrlEditor from './UrlEditor.js'
import {UrlModel, VideoMetaData, MapVideoModelToAppModel} from "./model.js"
import WebApi from './WebApi.js'

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
    var fetcher = new WebApi(data => {
      var table = []
      data.map(url => table.push(MapVideoModelToAppModel(url)))
      this.setState({loading: false, data: table})
    })

    fetcher.getVideoList()
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
