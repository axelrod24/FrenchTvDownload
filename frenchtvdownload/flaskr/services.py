from . import db
import time, threading
from main import getVideoMetadata
from DownloadException import FrTvDwnManifestUrlNotFoundError, FrTvDwnMetaDataParsingError, FrTvDwnPageParsingError, FrTvDwnVideoNotFound

def registerForDownload(theUrl):
    thedb = db.get_db().cursor()

    thedb.execute(
                'INSERT INTO url (prog_url, status) VALUES (?, ?)', (theUrl, "PENDING")
            )
    
    lastrowid = thedb.lastrowid

    # getting back the last inserted row
    row = thedb.execute("SELECT * FROM url WHERE id = '%s'" % lastrowid).fetchone()
    r = dict(row)

    callbackFct = lambda : download(r)
    threading.Timer(10, callbackFct).start()


def listDB():
    thedb = db.get_db()

    allUrls = []
    for row in thedb.execute('SELECT * FROM url').fetchall():
        print(dict(row))
        allUrls.append(dict(row))

    return allUrls


def download(r):
 
    # if not pending, terminate
    if r["status"] != "PENDING":
        return 

    print ("Will download: %s" % r["prog_url"])

    # callbackFct = lambda : download(index+1)
    # threading.Timer(5, callbackFct).start()
    
def fetchMetadata(url):
    try:
        progMetadata = getVideoMetadata(url)

    except FrTvDwnVideoNotFound:
        print("Can't find video: %s" % url)
        exit()

    except FrTvDwnPageParsingError:
        print("Can't get or parse video ID page: %s" % url)
        exit()
        
    except FrTvDwnManifestUrlNotFoundError:
        print("Can't parse video metadata: %s" % url)
        exit()

    except FrTvDwnMetaDataParsingError:
        print("Can't get manifest URL: %s" % url)
        exit()
    except:
        print("Unknown error getting metadata for %s" % url)
        exit() 

    thedb = db.get_db().cursor()

    # getting back the last inserted row
    row = thedb.execute("SELECT * FROM video WHERE prog_id = '%s'" % progMetadata["videoId"]).fetchone()

    # Video not yet downloaded
    if row is None:
        # write video meta and schedule download

    r = dict(row)

    return r    
    # callbackFct = lambda : download(r)
    # threading.Timer(10, callbackFct).start()


