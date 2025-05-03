from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .models import User  # Import relativo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/martinafabiani/sitomf/instance/gestione_ricette.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'somesecretkey'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'user_page'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def initialize_database():
    """Crea le tabelle del database se non esistono."""
    db.create_all()
