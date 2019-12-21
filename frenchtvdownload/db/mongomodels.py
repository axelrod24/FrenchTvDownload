from mongoengine import *
import datetime

MONGO_DB_NAME = "frtvdld"
MONGO_HOST = "dardos:27020"

connect(MONGO_DB_NAME, host=MONGO_HOST)

# def _is_in(val, ref):
#   if val not in val):
#     raise ValidationError('value should one of these field:', val)


class Errors(EmbeddedDocument):
  dateAdded = DateTimeField(default=datetime.datetime.utcnow)
  error = StringField()
  progCode = StringField()
  networkName = StringField()


class Channels(Document):
  url = StringField(required=True, unique=True)
  progCode = StringField(unique=True)
  networkName = StringField()
  dateAdded = DateTimeField(default=datetime.datetime.utcnow)
  displayName = StringField()
  dateLastChecked = DateTimeField()
  dateLastNewContent = DateTimeField()
  lastCheckedSuccessful = BooleanField()
  lastErrors = EmbeddedDocumentListField(Errors)


class Streams(Document):
  url = StringField(required=True, unique=True)
  progCode = StringField()
  networkName = StringField()
  dateAdded = DateTimeField(default=datetime.datetime.utcnow)
  # status = StringField(validation=_is_in(['pending', 'downloading', 'converting', 'done', 'error']))
  status = StringField()
  videoId = StringField()
  progMetadata = StringField()
  dateLastChecked = DateTimeField()
  lastErrors = EmbeddedDocumentListField(Errors)
  
class Videos(Document):
  path = StringField(required=True, unique=True)
  dateAdded = DateTimeField(default=datetime.datetime.utcnow)
  progCode = StringField()
  networkName = StringField()
  repo = StringField()
  filename = StringField()
  folder = StringField()
  codecs = StringField()
  title = StringField()
  duration = IntField()
  firstAirDate = DateTimeField()
  synopsis = StringField()
  stream = ReferenceField(Streams)
  




# C_DANS_LAIR = [
#   Streams(url="https://www.france.tv/france-5/c-dans-l-air/1109039-agriculteurs-consommateurs-le-grand-malaise.html", progCode="c_dans_l_air", networkName="https://www.france.tv/", status="pending"),
#   Streams(url="https://www.france.tv/france-5/c-a-vous/c-a-vous-saison-11/1109029-c-a-vous.html", progCode="c_a_vous", networkName="https://www.france.tv/", status="pending"),
#   Streams(url="https://www.france.tv/france-5/c-dans-l-air/1107813-c-dans-l-air.html", progCode="c_dans_l_air", networkName="https://www.france.tv/", status="pending"),
#   Streams(url="https://www.france.tv/france-5/c-a-vous/c-a-vous-saison-11/1107807-c-a-vous.html", progCode="c_a_vous", networkName="https://www.france.tv/", status="pending"),
#   Streams(url="https://www.france.tv/france-5/c-dans-l-air/1108073-c-dans-l-air.html", progCode="c_dans_l_air", networkName="https://www.france.tv/", status="pending"),
#   Streams(url="https://www.france.tv/france-5/c-a-vous/c-a-vous-saison-11/1108089-c-a-vous.html", progCode="c_a_vous", networkName="https://www.france.tv/", status="pending")
# ]

# for cdla in C_DANS_LAIR:
#   print("Save:", cdla)
#   cdla.save()



