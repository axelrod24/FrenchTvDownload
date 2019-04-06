import os, json
from flaskr.config import db
from flaskr import models
from frtvdld.download import get_video_metadata

ALL_VIDEO = [
    {"url": "https://www.france.tv/france-5/c-dans-l-air/942669-europeennes-les-candidats-descendent-dans-l-arene.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/941679-ghosn-retour-a-la-case-prison.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/939665-bouteflika-le-printemps-algerien-a-commence.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/939911-brexit-no-no-no-alors-no-deal.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/940217-les-lecons-d-un-remaniement-force.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-a-vous/c-a-vous-saison-10/942659-c-a-vous.html", "status": "pending"},
    {"url": "https://www.tf1.fr/tmc/quotidien-avec-yann-barthes/videos/quotidien-premiere-partie-29-mars-2019.html", "status": "pending"},
    {"url": "https://www.tf1.fr/tmc/quotidien-avec-yann-barthes/videos/quotidien-deuxieme-partie-29-mars-2019.html", "status": "pending"},
    {"url": "https://www.arte.tv/fr/videos/048268-001-A/crimes-a-la-cour-des-medicis-1-2/", "status": "pending"},
    {"url": "https://www.arte.tv/fr/videos/048268-002-A/crimes-a-la-cour-des-medicis-2-2/", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-a-vous/c-a-vous-saison-10/941649-c-a-vous.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/la-maison-france-5/937699-la-maison-france-5.html", "status": "pending"}
    ]

# Delete database file if it exists currently
db_path = os.path.join("flaskr","people.db")
if os.path.exists(db_path):
    os.remove(db_path)

# Create the database
db.create_all()

for video in ALL_VIDEO:
    metadata = get_video_metadata(video['url'])
    if metadata.manifestUrl is None:
        status = "not_available"
    else:
        status = "pending"

    data = models.add_new_video(url=video['url'], status=status, mdata=json.dumps(metadata._asdict()))
