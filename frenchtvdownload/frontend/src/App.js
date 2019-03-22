import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import UrlTable from './UrlTable.js';
import UrlEditor from './UrlEditor.js';

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      data: this.props.urlist
    }

    this.onAddUrl = this.onAddUrl.bind(this)
  }

  componentDidMount()
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
        <UrlTable ref="_urltable" data={this.state.data}/>
      </div>
    );
  }

  onAddUrl(url) {
    this.urlTable.addUrl(url)
  }
}

export default App;
