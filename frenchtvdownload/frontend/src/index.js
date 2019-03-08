import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';

class UrlModel {
    constructor(url, status) {
        this.url = url ;
        this.status = status ;
    }
} 

var AllUrls =[
    new UrlModel("https://www.france.tv/documentaires/art-culture/910287-la-petite-histoire-des-super-heros.html", "pending"),
    new UrlModel("https://www.france.tv/documentaires/science-sante/910533-haut-le-corps.html", "done"),
    new UrlModel("https://www.france.tv/documentaires/politique/874585-guyane-la-frontiere-invisible.html", "pending"),
    new UrlModel("https://www.france.tv/documentaires/societe/911315-le-sexisme-en-politique-un-mal-dominant.html", "pending"),
]


ReactDOM.render(<App urlist={AllUrls} />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();
