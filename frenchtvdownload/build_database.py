import os
from config import db
from models import Person, Video

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
]

# Delete database file if it exists currently
if os.path.exists("people.db"):
    os.remove("people.db")

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
