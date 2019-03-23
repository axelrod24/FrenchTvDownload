import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import {UrlModel, VideoMetaData} from "./model.js"


var AllUrls =[
    UrlModel(5, "https://www.france.tv/documentaires/art-culture/910287-la-petite-histoire-des-super-heros.html", "pending", 1551913200.0,
        VideoMetaData("https://ios-q1-ssl.tf1.fr/2/USP-0x0/07/89/13620789/ssm/13620789.ism/13620789.m3u8?e=1552203278&amp;max_bitrate=1500000&amp;st=ycJXVYakBvN79p6bW-hYPg&amp;vk=MTM2MjA3ODkubTN1OA%3D%3D",
            "Pour le quatrième numéro de «L'Emission politique», Léa Salamé reçoit Marine Le Pen, présidente du Rassemblement national. A quelques semaines du scrutin européen, les sondages sont favorables au parti de celle qui était au deuxième tour de l'élection présidentielle. Mais sa position sur l'Europe n'est pas toujours claire. Les diverses rubriques de l'émission permettent d'en savoir plus. «Le Film de l'actualité» de Thomas Sotto aborde avec l'invitée les temps forts de l'actualité. Dans le «Grand Débat», elle est confrontée à des Français et des membres de la société civile. Au programme également : le «Face-à-face politique» et le reportage «Sans filet» de Guillaume Daret. Nathalie Saint-Cricq, chef du service politique de France Télévisions, intervient en fin d'émission, ainsi que Jean-Baptiste Marteau, qui donne le verdict du sondage.",
            "L'emission politique",
            "20190314-l_emission_politique",
            "hls",
            2100,
            "http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion=92303955-6487-4c1c-a937-6cc468af5f49",
            false,
            1551913200.0,
            "emission politique")
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
