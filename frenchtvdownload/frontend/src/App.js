import React, { Component } from 'react'
// import logo from './logo.svg'
import './App.css'
import UrlTable from './UrlTable.js'
import UrlEditor from './UrlEditor.js'
import { MapVideoModelToAppModel } from "./model.js"
import WebApi from './WebApi.js'
import store from "./redux/store";

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: true,
    }
    
    this.store = store
    this.onAddUrl = this.onAddUrl.bind(this)
  }

  componentDidMount()
  {
    console.log("App:componentDidMount")
    var fetcher = new WebApi(data => {
      var table = []
      data.map(video => this.store.dispatch({type:"ADD_URL", payload:MapVideoModelToAppModel(video)}))
      this.setState({loading: false})
    })

    fetcher.getVideoList()
  }

  componentDidUpdate(prevProps, prevState)
  {
    console.log("App:componentDidUpdate")
    const { _urleditor, _urltable } = this.refs
    this.urlEditor = _urleditor
    this.urlTable = _urltable
  }

  render() {
    console.log("App:render")
    console.log("App:store:", this.store)
    console.log("App:store.state:", this.store.getState())
    return (
      <div className="container">
        <h1 className="banner">FrenchTV Download List of Url</h1>
        <UrlEditor ref="_urleditor" onAddUrl={this.onAddUrl}/>
        {/* {(this.state.loading) ? <p> loading table</p> : <UrlTable ref="_urltable" store={this.store}/>} */}
        <UrlTable ref="_urltable" store={this.store}/>
      </div>
    );
  }

  onAddUrl(url) {
    this.urlTable.addUrl(url)
  }
}

export default App;
