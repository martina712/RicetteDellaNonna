# ========================
# Database Models
# ========================

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'utenti'
    id = db.Column(db.Integer, primary_key=True)
    nome_utente = db.Column(db.String(8), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(12), nullable=False)

    def __repr__(self):
        return f'<User {self.nome_utente}>'

    def get_id(self):
        return str(self.id)


class Recipe(db.Model):
    __tablename__ = 'ricette'
    nr = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    ingredienti = db.Column(db.Text, nullable=False)
    procedimento = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    utente_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    votes = db.relationship('Vote', backref='recipe', lazy='dynamic')

    @property
    def media_voto(self):
        total_votes = self.votes.count()
        if total_votes > 0:
            return sum(vote.voto for vote in self.votes) / total_votes
        return 0


class Comment(db.Model):
    __tablename__ = 'commenti'
    id = db.Column(db.Integer, primary_key=True)
    recipe_nr = db.Column(db.Integer, db.ForeignKey('ricette.nr'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), nullable=False)
    commento = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())


class Vote(db.Model):
    __tablename__ = 'voti'
    recipe_nr = db.Column(db.Integer, db.ForeignKey('ricette.nr'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), primary_key=True)
    voto = db.Column(db.Integer, nullable=False)


class Favorite(db.Model):
    __tablename__ = 'preferiti'
    utente_id = db.Column(db.Integer, db.ForeignKey('utenti.id'), primary_key=True)
    recipe_nr = db.Column(db.Integer, db.ForeignKey('ricette.nr'), primary_key=True)




