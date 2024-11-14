"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Characters
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    print(users)# users es una lista con todos los usuarios
    users_serialized = []
    for user in users:
        users_serialized.append(user.serialize())
    #serializar es convertir un dato tipo modelo a dict
    #solo asi se puede convertir en JSON
    return jsonify({'msg': 'ok', 'data': users_serialized}), 200

@app.route('/planet', methods=['POST'])
def post_planet():
    #para crear un planeta necesitamos un body que contenga
    #el nombre y el clima del planeta
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body:
        return jsonify({'msg': 'El campo name es obligatorio'}), 400
    if 'climate' not in body:
        return jsonify({'msg': 'El campo climate es obligatorio'}), 400
    new_planet = Planet()
    new_planet.name = body['name']
    new_planet.climate = body['climate']
    db.session.add(new_planet)
    db.session.commit()

    return jsonify(
        {
            'msg': 'Planeta agregado con exito',
          'data': new_planet.serialize()
          }
          ), 201


@app.route('/characters/<int:id>', methods=['GET'])
def get_characters(id):
    character = Characters.query.get(id)
    print(character) #objeto
    print(character.name)
    print(character.planet_id)
    print(character.planet_id_relationship) #objeto
    print(character.planet_id_relationship.name)
    character_serialized = character.serialize()
    #character_serialized['planet_info'] = character.planet_id_relationship.serialize()
    return jsonify({
        'msg': 'ok',
        'data': character_serialized
        })

@app.route('/favorite_planets/<int:user_id>', methods=['GET'])
def get_favorites_by_user(user_id):
    user = User.query.get(user_id)
    #print(user)
    #print(user.planet_favorites)
    favorite_planets_serialized = []
    for fav_planet in user.planet_favorites:
        favorite_planets_serialized.append(fav_planet.planet_relationship.serialize())
    data = {
        'user_info': user.serialize(),
        'planets_favorites': favorite_planets_serialized
    }
    return jsonify({'msg':'ok', 'data': data})

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
