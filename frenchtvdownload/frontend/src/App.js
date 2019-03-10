import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import UrlTable from './UrlTable.js';

class App extends Component {
  render() {
    return (
      <div className="container">
        <h1 className="banner">FrenchTV Download List of Url</h1>
        <UrlTable data={this.props.urlist}/>
      </div>
    );
  }
}

export default App;
