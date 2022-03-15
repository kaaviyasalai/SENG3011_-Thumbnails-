from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
  
connection_url = 'mongodb+srv://thumbnails:thumbnails.@cluster0.lfkm3.mongodb.net/SENG3011?retryWrites=true&w=majority'
app = Flask(__name__)
client = pymongo.MongoClient(connection_url)

Database = client.get_database('SENG3011')

Table = pymongo.collection.Collection(Database, 'SENG3011_collection')

@app.route('/find', methods=['GET'])
def find():
    query = Table.find()
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
    query = Table.find_one(queryObject)
    query.pop('_id')
    return jsonify(query)

if __name__ == '__main__':
    app.run(port=8000)

