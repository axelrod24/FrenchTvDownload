import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import {UrlModel, VideoMetaData} from "./model.js"


var AllUrls =[
    UrlModel(5, "https://www.france.tv/documentaires/art-culture/910287-la-petite-histoire-des-super-heros.html", "pending", 1551913200.0,
        VideoMetaData("https://ios-q1-ssl.tf1.fr/2/USP-0x0/07/89/13620789/ssm/13620789.ism/13620789.m3u8?e=1552203278&amp;max_bitrate=1500000&amp;st=ycJXVYakBvN79p6bW-hYPg&amp;vk=MTM2MjA3ODkubTN1OA%3D%3D",
            "quotidien-premiere-partie-du-7-mars-2019",
            "20190307-Tf1-quotidien-premiere-partie-du-7-mars-2019",
            "hls",
            2100,
            "https://delivery.tf1.fr/mytf1-wrd/13620789",
            false,
            1551913200.0,
            "quotidien")
    ),

    UrlModel(6, "https://www.france.tv/documentaires/science-sante/910533-haut-le-corps.html", "done",1551913200.0,
        VideoMetaData("the/manifest/url/2",
        "prog title_2",
        "the_filename_2",
        "hls",
        2100,
        "the-video-id_2",
        false,
        1551913200.0,
        "Haut le corps")
    ),

    UrlModel(9, "https://www.france.tv/documentaires/politique/874585-guyane-la-frontiere-invisible.html", "pending",1551913200.0,
        VideoMetaData("the/manifest/url/3",
        "prog title_3",
        "the_filename_3",
        "hls",
        2100,
        "the-video-id_3",
        false,
        1551913200.0,
        "guyane-la-frontiere-invisible")
        ),

    UrlModel(11, "https://www.france.tv/documentaires/societe/911315-le-sexisme-en-politique-un-mal-dominant.html", "pending",1551913200.0,
        VideoMetaData("the/manifest/url/4",
        "prog title_4",
        "the_filename_4",
        "hls",
        2100,
        "the-video-id_4",
        false,
        1551913200.0,
        "le-sexisme-en-politique-un-mal-dominant")
    )
]

ReactDOM.render(<App urlist={AllUrls} />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();
