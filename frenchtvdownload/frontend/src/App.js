import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import AddUrlButton from './Button.js';
import UrlTable from './UrlTable.js';

class App extends Component {
  render() {
    return (
      <div className="container">
      <h1 className="banner">FrenchTV Download List of Url</h1>
      <div className="editor">
        <label htmlFor="url" style={{width: '80%'}}>Url :
          <input id="url" type="text" style={{width: '80%'}}/>
          <AddUrlButton />
        </label>

          {/* <label for="url" >Url :
          </label>
          <button id="addurl">Add</button> */}
      </div>
      <UrlTable data={this.props.urlist}/>
{/* 
      <div class="people">
          <table>
              <caption>List of Url</caption>
              <thead>
                  <tr>
                      <th>url</th>
                      <th>status</th>
                      <th>timestamp</th>
                      <th>action</th>
                  </tr>
              </thead>
              <tbody>
              </tbody>
          </table>
      </div> */}
      <div className="error">
      </div>
  </div>
    );
  }
}

export default App;
