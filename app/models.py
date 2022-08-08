from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime as dt


user_pokemon = db.Table(
    'user_pokemon',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('pokemon_id', db.Integer, db.ForeignKey('pokemon.id')),
)

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    password = db.Column(db.String)
    created_on = db.Column(db.DateTime, default=dt.utcnow)

    owning = db.relationship('Pokemon', secondary=user_pokemon, backref="masters", lazy="dynamic")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self) 
        db.session.commit() 
    
    def delete(self):
        db.session.delete(self) 
        db.session.commit() 

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def catch_poke(self, poke_to_catch):
        self.owning.append(poke_to_catch)
        db.session.commit()

    def release_poke(self, poke_to_rel):
        self.owning.remove(poke_to_rel)
        db.session.commit()

    def check_user_has_poke(self, poke_to_check):
        return poke_to_check in self.owning



@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# POKEMON ######################################################################
class Pokemon(db.Model):
    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    pokemon_id_original = db.Column(db.String)
    ability = db.Column(db.String)
    defense = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    hp = db.Column(db.Integer)
    gif = db.Column(db.String)
    image = db.Column(db.String)
    
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def poke_to_db(self, poke_dict):
        self.name = poke_dict["name"]
        self.pokemon_id_original = poke_dict["pokemon_id_original"]
        self.ability = poke_dict["ability"]
        self.attack = poke_dict["attack"]
        self.hp = poke_dict["hp"]
        self.defense = poke_dict["defense"]
        self.gif = poke_dict["gif"]
        self.image = poke_dict["image"]
    
    def __repr__(self):
        return '<Pokemon {}>'.format(self.name)
   
        
    def save(self):
        db.session.add(self) 
        db.session.commit() 

    def delete(self):
        db.session.delete(self) 
        db.session.commit() 