"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
Commands:
pipenv install flask
pipenv shell
python src/app.py
***Para verificar si algun puerto sigue activo:
lsof -i :3000
***Para eliminar el puerto:
kill -9 <PID>
***
psql -h localhost -U gitpod example
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Characters, Planet_Favorites, Characters_Favorites

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


#    [GET] /users Listar todos los usuarios del blog.

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

#     [POST] /favorite/planet/<int:planet_id>/<int:user_id>
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

@app.route('/character', methods=['POST'])
def post_character():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar información en el body'}), 400
    if 'name' not in body:
        return jsonify({'msg': 'El campo name es obligatorio'}), 400
    if 'height' not in body:
        return jsonify({'msg': 'El campo height es obligatorio'}), 400
    if 'planet_id' not in body:
        return jsonify({'msg': 'El campo planet_id es obligatorio'}),400 
    new_character = Characters()
    new_character.name = body['name']
    new_character.height = body['height']
    new_character.planet_id = body['planet_id']
    db.session.add(new_character)
    db.session.commit()

    return jsonify(
        {
            'msg': 'El personaje ha sido agregado con exito',
          'data': new_character.serialize()
          }
          ), 201


#   [GET] /planets Listar todos los registros de planets en la base de datos.
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    print("ACA ESTAN LOS PLANETS: ",planets)
    planets_serialized = []
    for planet in planets:
        planets_serialized.append(planet.serialize())
    return jsonify({'msg': 'Planetas traidos exitosamente', 'data': planets_serialized}), 200

#   [GET] /planets/<int:planet_id> Muestra la información de un solo planeta según su id.
@app.route('/planets/<int:id>', methods=['GET'])
def get_planets(id):
    planet = Planet.query.get(id)
    print(planet) #objeto
    planet_serialized = planet.serialize()
    return jsonify({
        'msg': 'ok',
        'data': planet_serialized
        })


#  [GET] /people/<int:people_id> Muestra la información de un solo personaje según su id.
@app.route('/characters/<int:id>', methods=['GET'])
def get_characters(id):
    character = Characters.query.get(id)
    print(character) #objeto
    print(character.name)
    print(character.planet_id)
    print(character.planet_id_relationship) #objeto
    print(character.planet_id_relationship.name)
    character_serialized = character.serialize()
    return jsonify({
        'msg': 'ok',
        'data': character_serialized
        })
#   [GET] /people Listar todos los registros de people en la base de datos.
@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Characters.query.all()
    print(characters)
    characters_serialized = []
    for character in characters:
        characters_serialized.append(character.serialize())
    return jsonify({
        'msg': 'ok',
        'data': characters_serialized
        })


@app.route('/users', methods=['POST'])
def create_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "El cuerpo de la solicitud está vacío"}), 400
    if 'email' not in body:
        return jsonify({"msg": "El campo 'email' es obligatorio"}), 400
    if 'password' not in body:
        return jsonify({"msg": "El campo 'password' es obligatorio"}), 400
    if 'is_active' not in body:
        return jsonify({"msg": "El campo 'is_active' es obligatorio"}), 400
    
    new_user = User(
        email=body['email'],
        password=body['password'],
        is_active=body['is_active']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'msg':'Usuario creado exitosamente', 'data': new_user.serialize()}), 201

# [GET] /users/<int:user_id>/favorites Listar todos los favoritos que pertenecen al usuario actual.
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_all_user_favorites(user_id):
    characters_favorites = Characters_Favorites.query.filter_by(user_id=user_id).all()
    characters_favorites_serialized = []
    planet_favorites = Planet_Favorites.query.filter_by(user_id=user_id).all()
    planet_favorites_serialized = []
    for planet in planet_favorites:
        planet_favorites_serialized.append(planet.serialize())
    for character in characters_favorites:
        characters_favorites_serialized.append(character.serialize())
    return jsonify({'msg': 'Planetas y Personajes favoritos traidos exitosamente', 'Aqui estan los planetas favoritos: ': planet_favorites_serialized, 'Aqui estan los personajes favoritos: ': characters_favorites_serialized}), 200

#    [POST] /favorite/planet/<int:planet_id>/<int:user_id> Añade un nuevo planet favorito al usuario actual con el id = planet_id.
@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['POST'])
def add_new_favorite_planet(planet_id, user_id):
        planets = Planet.query.all()
        planet =Planet.query.get(planet_id)
        user = User.query.get(user_id)
        if user and planet:
            relation_favorite = Planet_Favorites.query.filter_by(user_id=user_id,planet_id=planet_id).first()
            if relation_favorite != True:
                db.session.add(planet_id,user_id)
                db.session.commit(relation_favorite)
                return jsonify({'msg': 'El planeta ha sido agregado como favorito', 'lista de planetas: ': planets}), 201
            else:
                return jsonify({'msg': 'El planeta ya esta agregado como favorito'}), 400


# [DELETE] /favorite/planet/<int:planet_id>/<int:user_id> Elimina un planet favorito con el id = planet_id.
   
@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id, user_id):
    planet_favorites_serialized = []
    planet_to_be_deleted = Planet.query.get(planet_id)
    user  = User.query.get(user_id)
    if not user:
        return jsonify({'msg': f'El usuario con ID {user_id} no existe'}), 404
    if not planet_to_be_deleted:
        return jsonify({'msg': f'El planeta con ID {planet_id} no existe'}), 404
    relation_favorite = Planet_Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if relation_favorite:
        db.session.delete(relation_favorite)
        db.session.commit()
        planet_favorites = Planet_Favorites.query.all()
        for planet in planet_favorites:
            planet_favorites_serialized.append(planet.serialize())
        return jsonify({'msg': 'El planeta ha sido eliminado de tus favoritos', 'lista actual de planetas: ': planet_favorites_serialized}), 200
    else:
        return jsonify({'msg': 'El planeta no estaba en la lista de favoritos'}), 404
    
# [DELETE] /favorite/people/<int:people_id>/<int:user_id> Elimina un people favorito con el id = people_id
@app.route('/favorite/people/<int:character_id>/<int:user_id>', methods=['DELETE'])
def delete_favorite_character(character_id, user_id):
    characters_favorites_serialized = []
    user  = User.query.get(user_id)
    if not user:
        return jsonify({'msg': f'El usuario con ID {user_id} no existe'}), 404
    relation_favorite = Characters_Favorites.query.filter_by(user_id=user_id, character_id=character_id).first()
    if relation_favorite:
        db.session.delete(relation_favorite)
        db.session.commit()
        characters_favorites = Characters_Favorites.query.all()
        for character in characters_favorites:
            characters_favorites_serialized.append(character.serialize())
        return jsonify({'msg': 'El personaje ha sido eliminado de tus favoritos', 'lista actual de personaje: ': characters_favorites_serialized}), 200
    else:
        return jsonify({'msg': 'El personaje no estaba en la lista de favoritos'}), 404

#[POST] /favorite/people/<int:people_id>/<int:user_id> Añade un nuevo people favorito al usuario actual con el id = people_id.
@app.route('/favorite/people/<int:character_id>/<int:user_id>', methods=['POST'])
def add_new_favorite_character(character_id,user_id):
    characters_favorites_serialized = []
    character_to_be_added = Characters.query.get(character_id)
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': f'El usuario con ID {user_id} no existe'}), 404
    if not character_to_be_added:
        return jsonify({'msg': f'El personaje con el ID {character_id} no existe'}), 404
    relation_favorite = Characters_Favorites.query.filter_by(user_id=user_id,character_id=character_id).first()
    if not relation_favorite:
        new_favorite = Characters_Favorites(user_id=user_id, character_id=character_id)
        db.session.add(new_favorite)
        db.session.commit()
        characters_favorites = Characters_Favorites.query.all()
        for character in characters_favorites:
            characters_favorites_serialized.append(character.serialize())
        return jsonify({'msg': 'El personaje ha sido agregado staisfactoriamente', 'lista actual de personajes favoritos': characters_favorites_serialized})
    else: 
        return jsonify({'msg': 'El personaje ya esta agregado en tu lista de personajes favoritos'}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
