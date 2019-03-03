import os
from flaskr.config import db
from flaskr.models import Person, Video

# Data to initialize database with
PEOPLE = [
    {"fname": "Doug", "lname": "Farrell"},
    {"fname": "Kent", "lname": "Brockman"},
    {"fname": "Bunny", "lname": "Easter"},
]

ALL_URL = [
    {"url": "https://www.france.tv/series-et-fictions/telefilms/832397-mystere-place-vendome.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/832347-petitions-en-ligne-ric-des-outils-democratiques.html", "status": "done"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/832583-c-dans-l-air.html", "status": "done"},
    {"url": "https://www.france.tv/france-3/cassandre/cassandre-saison-3/897829-loup-gris.html", "status": "pending"},
    {"url": "https://www.france.tv/france-2/tout-compte-fait/887251-decathlon-les-secrets-d-un-champion.html", "status": "pending"},
    {"url": "https://www.france.tv/france-2/on-n-est-pas-couche/on-n-est-pas-couche-saison-13/898067-on-n-est-pas-couche.html", "status": "pending"}
]

# Delete database file if it exists currently
db_path = os.path.join("flaskr","people.db")
if os.path.exists(db_path):
    os.remove(db_path)

# Create the database
db.create_all()

# iterate over the PEOPLE structure and populate the database
for person in PEOPLE:
    p = Person(lname=person.get("lname"), fname=person.get("fname"))
    db.session.add(p)

for url in ALL_URL:
    v = Video(url=url.get("url"), status=url.get("status"))
    db.session.add(v)

db.session.commit()
