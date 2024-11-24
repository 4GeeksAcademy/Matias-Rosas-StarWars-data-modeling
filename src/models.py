from flask_sqlalchemy import SQLAlchemy

"""
Cualquier cambio hecho en alguna de las tablas se debe hacer
pipenv run migrate
pipenv run upgrade
"""

db = SQLAlchemy()

#     user_relationship = db.relationship('User', back_populates='characters_favorites')


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    planet_favorites = db.relationship('Planet_Favorites', back_populates='user_relationship')
    characters_favorites = db.relationship('Characters_Favorites', back_populates='user_relationship')

    def __repr__(self):
        return f'Usuario {self.email} y id {self.id}'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "password": self.password
            # do not serialize the password, its a security breach
        }
#    character_relationship = db.relationship('Characters', back_populates='characters_favorites')

class Characters(db.Model):
    __tablename__ = "characters"
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=False)
    planet_id_relationship = db.relationship('Planet', back_populates='people')
    characters_favorites = db.relationship('Characters_Favorites', back_populates='character_relationship')

    def __repr__(self):
        return f'Character {self.name} con ID {self.id}'
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'height': self.height,
            'planet_info': self.planet_id_relationship.serialize() #Convertimos el objeto de la tabla Planet en diccionario 
        }
#    planet_relationship = db.relationship('Planet', back_populates='favorite_planets')

class Planet(db.Model):
    __tablename__ = "planet"
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    climate = db.Column(db.String(50), nullable=False)
    people = db.relationship('Characters', back_populates='planet_id_relationship')
    favorite_planets = db.relationship('Planet_Favorites', back_populates='planet_relationship')

    def __repr__(self):
        return f'Planeta {self.name} con clima {self.climate}'
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'climate': self.climate
        }

class Planet_Favorites(db.Model):
    __tablename__ = 'planet_favorites'
    id = db.Column(db.Integer, primary_key= True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship('User', back_populates='planet_favorites')
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'))
    planet_relationship = db.relationship('Planet', back_populates='favorite_planets')

    def __repr__(self):
        return f'Al usuario {self.user_id}, le gusta el planeta {self.planet_id}'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'planet_id': self.planet_id
        }

class Characters_Favorites(db.Model):
    __tablename__ = 'characters_favorites'
    id = db.Column(db.Integer, primary_key= True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship('User', back_populates='characters_favorites')
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    character_relationship = db.relationship('Characters', back_populates='characters_favorites')

    def __repr__(self):
        return f'Al usuario {self.user_id}, le gusta el personaje {self.character_id}'
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'character_id': self.character_id
        }        