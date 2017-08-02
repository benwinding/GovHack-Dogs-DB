from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

e = create_engine('sqlite:///parks.db')

app = Flask(__name__)
api = Api(app)

import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('cert.pem', 'privkey.pem')

class Parks(Resource):
    def get(self):
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        conn = e.connect()
        query = conn.execute("SELECT _rowid_, ParkName, lat, lng \
                              FROM parksdata \
                              WHERE activities__Dogwalking = 'TRUE'")
        data = []
        for c in query.cursor:
            distance = (float(c[2]) - float(lat))**2 + (float(c[3]) - float(lng))**2
            data.append({'parkid': c[0], 'ParkName':c[1], 'lat':c[2], 'lng':c[3], 'distance':distance})

        data.sort(key=lambda x: x['distance'])

        return {'data':data[:10]}, {'Content-Type': 'application/json', 'Access-Control-Allow-Origin':'*'}

class Park(Resource):
    def get(self):
        id = request.args.get('parkid')
        conn = e.connect()
        query = conn.execute("SELECT ParkName, lat, lng, facilities__Toilet, 'facilities__Toilet(accessible)', facilities__Babychangeroom, facilities__Shower, facilities__Parking, facilities__Boatramp, facilities__Shelter, facilities__Picnictable, facilities__Playground, facilities__Sportsfield, facilities__Cafe, facilities__Publictransportaccess, facilities__BBQfacilities\
                              FROM parksdata\
                              WHERE _rowid_ =" + id)
        return {'data': [dict(zip(tuple (query.keys()), i)) for i in query.cursor]}, {'Content-Type': 'application/json', 'Access-Control-Allow-Origin':'*'}

class Stats(Resource):
    def get(self):
        sub = request.args.get('suburb')
        sub = sub.lower()
        conn = e.connect()
        query = "SELECT COUNT(Breed), Breed FROM (SELECT Breed FROM stats WHERE Suburb = \""+sub+"\") GROUP BY Breed"
        print query
        breeds = conn.execute(query)
        return {'data': [dict(zip(tuple(breeds.keys()), i)) for i in breeds.cursor]}, {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}

class ParkStats(Resource):
    def get(self):
        park = request.args.get('parkid')
        conn = e.connect()
        reviews = conn.execute("SELECT username, rating, comment\
                                FROM reviews\
                                WHERE parkid = "+park)


        return {'data': [dict(zip(tuple(reviews.keys()), i)) for i in reviews.cursor]}, {'Content-Type': 'application/json','Access-Control-Allow-Origin': '*'}

api.add_resource(Parks, '/parks')
api.add_resource(Park, '/park')
api.add_resource(Stats, '/dogstats')
api.add_resource(ParkStats, '/reviews')


if __name__ == '__main__':
    app.run(host='0.0.0.0', ssl_context=context)
