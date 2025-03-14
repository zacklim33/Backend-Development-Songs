from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}:{mongodb_port}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}:{mongodb_port}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))


#######################################################################
# Ex1: Implementing /health and /count 
#######################################################################
# to implement /health endpoint
@app.route("/health", methods=["GET"] )
def health():
    return jsonify(dict(status="ok")), 200


# return how many documents in song collection
@app.route("/count", methods=["GET"])
def getCount():
    docCount=db.songs.count_documents({})
    return {"count": int(docCount)}, 200


#######################################################################
# Ex2: Return all songs in collection
#######################################################################
@app.route("/song",methods=["GET"])
def songs():
    results=db.songs.find({})
    dbSongs = list(results)
    if not results or len(dbSongs) < 1:
        return json_util.dumps(dbSongs), 404

    return json_util.dumps(dbSongs), 200


#######################################################################
# Ex3: Get a song
#######################################################################
@app.route("/song/<int:id>", methods=["GET"])
def get_song_by_id(id):
    result=db.songs.find_one({"id":id})
    # dbSong=list(result)
    if not result:
        return ( {"message": f"song with id({id}) not found"}, 404)
    
    return (parse_json(result), 200)


#######################################################################
# Ex4: Create a song
#######################################################################
@app.route("/song/", methods=["POST"])
def create_song():
    
    # get and check for json input in HTTP header
    inputData=request.get_json()
    if not inputData:
        return ({"message": "Missing or invalid JSON input"}, 422)
    
    song=db.songs.find_one({"id":inputData['id']} )
    
    #song exists in DB 
    if song :
        return {"message":f"song with id {song['id']} already present"}, 302

    try:
        insertResult = db.songs.insert_one(inputData)
    except NameError:
        return ({"message": "Problem in adding data into collection"}, 500)
    
    return ( {"message": parse_json(insertResult.inserted_id) }, 201)



##########################################################################
# Ex5: Updating a song using PUT method
##########################################################################
@app.route("/song/<int:id>", methods=["PUT"])
def update_song(id):
    
    # check if 
    inputData=request.get_json()
    if not inputData:
        return ({"message": "INPUT JSON is problematic"}, 422)    
    
    result=db.songs.find_one({"id": id})
    
    if not result:
        return ( {"message": f"song with id({id}) not found"}, 404)    
    
    try:
        update_result = db.songs.update_one( {"id": id}, 
            { '$set': { 'lyrics': inputData['lyrics'], 'title': inputData['title'] } 
             })
        
    except NameError:
        return ( {"message": "Internal server error"}, 500)    

    if update_result.modified_count == 0:
        return ( {"message": f"song ID ({id}) found, but nothing updated"}, 200)    
    else:
        return ( parse_json(db.songs.find_one({"id":id})), 201)
    


##########################################################################
# Ex6: Delete a song using DELETE HTTP method
##########################################################################
@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):
          
    result=db.songs.find_one({"id": id})
    
    if not result:
        return ( {"message": f"song with id({id}) not found"}, 404)
        
    try:
        update_result = db.songs.delete_one( {"id": id} )
        
    except NameError:
        return ( {"message": "Internal server error"}, 500)
    
    if update_result.deleted_count == 0:
        return ( {"message": "Nothing was deleted"}, 404)    
    else:
        return ({"message": f"Song id({id}) was deleted"}, 204)
