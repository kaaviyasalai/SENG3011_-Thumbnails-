from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
  
cluster = "mongodb+srv://thumbnails:thumbnails@cluster0.lfkm3.mongodb.net/SENG3011?retryWrites=true&w=majority"
application = Flask(__name__)
client = MongoClient(cluster)

db = client.SENG3011

collection = db.SENG3011_collection

@app.route('/find', methods=['GET'])
def find():
    query = collection.find({})

    output = {}
    i = 0 
    for x in query:
        output[i] = x
        output[i].pop('_id')
        i+=1
    return jsonify(output)

@app.route('/find-one/<argument>/<value>/', methods=['GET'])
def findOne(argument, value):
    queryObject = {argument: value}
    query = collection.find_one(queryObject)
    query.pop('_id')
    return jsonify(query)

if __name__ == '__main__':
    app.run(port=8000)

