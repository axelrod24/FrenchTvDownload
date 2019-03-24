import os
from flaskr.config import db
from flaskr.models import Person, VideoModel

# Data to initialize database with
PEOPLE = [
    {"fname": "Doug", "lname": "Farrell"},
    {"fname": "Kent", "lname": "Brockman"},
    {"fname": "Bunny", "lname": "Easter"},
]

ALL_URL = [
    {"url": "https://www.france.tv/documentaires/art-culture/929817-daho-par-daho.html", "status": "pending"},
    {"url": "https://www.france.tv/series-et-fictions/telefilms/927913-un-homme-parfait.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/929925-c-dans-l-air.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/929133-elysee-senat-ca-chaufe.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/927697-violences-et-maintenant-l-armee.html", "status": "pending"},
    {"url": "https://www.france.tv/france-5/c-dans-l-air/927977-europe-la-tentation-populiste.html", "status": "pending"},
    {"url": "https://www.france.tv/france-2/un-si-grand-soleil/un-si-grand-soleil-saison-1/930031-un-si-grand-soleil.html", "status": "pending"}
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
    v = VideoModel(url=url.get("url"), status=url.get("status"))
    db.session.add(v)

db.session.commit()
