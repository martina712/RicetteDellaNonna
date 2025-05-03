# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from urllib.parse import unquote
import os
from werkzeug.utils import secure_filename
from models import User, Recipe, Comment, Vote, Favorite  # Importa tutti i modelli
import logging

logging.basicConfig(level=logging.INFO)
print("Starting Flask application...")

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/gestione.ricette.sqlite'
app.config['SECRET_KEY'] = 'somesecretkey'  # Replace with a secure key for production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = '/Users/martinafabiani/sitomf/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize the database
db = SQLAlchemy(app)

# Initialize the login manager
login_manager = LoginManager(app)
login_manager.login_view = 'user_page'  # Redirect here if login required

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_first_request
def create_upload_folder():
    """Crea automaticamente la directory di upload se non esiste."""
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"Directory creata: {app.config['UPLOAD_FOLDER']}")

@app.before_request
def log_request():
    logging.info(f"Request: {request.method} {request.url}")

# ========================
# Routes
# ========================

@app.route('/')
def index():
    print("Rendering index page...")
    # Query top 5 recipes (by average vote) for the homepage footer.
    top_recipes = (
        Recipe.query
        .outerjoin(Vote)
        .group_by(Recipe.nr)
        .order_by(func.avg(Vote.voto).desc())
        .limit(5)
        .all()
    )
    print(f"Top recipes: {top_recipes}")
    return render_template('index.html', top_recipes=top_recipes)

@app.route('/utente')
def user_page():
    if current_user.is_authenticated:
        user_recipes = Recipe.query.filter_by(utente_id=current_user.id).all()
        return render_template('utente.html', user_recipes=user_recipes)
    else:
        return render_template('utente.html')

@app.route('/login', methods=['POST'])
def login():
    nome_utente = request.form.get('nome_utente')
    password = request.form.get('password')
    user = User.query.filter_by(nome_utente=nome_utente, password=password).first()
    if user:
        login_user(user)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('user_page'))
    else:
        flash('Invalid credentials', 'danger')
        return redirect(url_for('user_page'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        nome_utente = request.form.get('nome_utente')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(nome_utente=nome_utente).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        new_user = User(nome_utente=nome_utente, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('user_page'))
    return render_template('register.html')

@app.route('/fav')
@login_required
def favorites():
    favorites = (
        db.session.query(Recipe)
        .join(Favorite, Recipe.nr == Favorite.recipe_nr)
        .filter(Favorite.utente_id == current_user.id)
        .all()
    )
    return render_template('fav.html', favorites=favorites)

@app.route('/nuovaricetta', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        title = request.form.get('title')
        ingredienti = request.form.get('ingredienti')
        procedimento = request.form.get('procedimento')
        tipo = request.form.get('tipo')
        image = request.files.get('image')
        image_path = request.files.get('image_path')

        try:
            # Salva l'immagine se presente
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f'uploads/{filename}'

            # Crea una nuova ricetta
            new_recipe = Recipe(
                title=title,
                ingredienti=ingredienti,
                procedimento=procedimento,
                tipo=tipo,
                image_path=image_path,
                utente_id=current_user.id
            )

            # Aggiungi la ricetta al database
            db.session.add(new_recipe)
            db.session.commit()
            flash('Ricetta aggiunta con successo!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()  # Annulla eventuali modifiche in caso di errore
            flash(f'Errore durante l\'aggiunta della ricetta: {str(e)}', 'danger')
            return redirect(url_for('add_recipe'))

    return render_template('nuovaricetta.html')

@app.route('/edit_recipe/<int:recipe_nr>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_nr):
    recipe = Recipe.query.get_or_404(recipe_nr)

    if recipe.utente_id != current_user.id:
        flash('Non sei autorizzato a modificare questa ricetta.', 'danger')
        return redirect(url_for('user_page'))

    if request.method == 'POST':
        recipe.title = request.form.get('title')
        recipe.ingredienti = request.form.get('ingredienti')
        recipe.procedimento = request.form.get('procedimento')
        recipe.tipo = request.form.get('tipo')

        image = request.files.get('image')
        remove_image = request.form.get('remove_image')
        try:
            if remove_image == 'on' and recipe.image_path:
                full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], recipe.image_path.split('/')[-1])
                if os.path.exists(full_image_path):
                    os.remove(full_image_path)
                recipe.image_path = None

            if image and allowed_file(image.filename):
                if recipe.image_path:
                    full_image_path = os.path.join(app.config['UPLOAD_FOLDER'], recipe.image_path.split('/')[-1])
                    if os.path.exists(full_image_path):
                        os.remove(full_image_path)

                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                recipe.image_path = f'uploads/{filename}'
            db.session.commit()
            flash('Ricetta modificata con successo!', 'success')
            return redirect(url_for('user_page'))
        except Exception as e:
            flash(f'Errore durante la modifica della ricetta: {str(e)}', 'danger')
            return redirect(url_for('edit_recipe', recipe_nr=recipe_nr))
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/search')
def search():
    query = request.args.get('query')
    recipes = []
    if query:
        recipes = Recipe.query.filter(Recipe.title.ilike(f'%{query}%')).all()
    desserts = Recipe.query.filter_by(tipo='desserts').all()
    first_courses = Recipe.query.filter_by(tipo='first_courses').all()
    main_courses = Recipe.query.filter_by(tipo='main_courses').all()
    starters = Recipe.query.filter_by(tipo='starters').all()
    return render_template(
        'search.html',
        recipes=recipes,
        desserts=desserts,
        first_courses=first_courses,
        main_courses=main_courses,
        starters=starters,
    )

@app.route('/<title>', methods=['GET'])
def view_recipe(title):
    title = unquote(title)
    recipe = Recipe.query.filter_by(title=title).first_or_404()
    comments = Comment.query.filter_by(recipe_nr=recipe.nr).order_by(Comment.created_at.desc()).all()
    avg_vote = recipe.media_voto  # Calcola il voto medio usando la proprietà aggiornata
    return render_template('ricetta.html', recipe=recipe, comments=comments, avg_vote=avg_vote)

@app.route('/<title>/comment', methods=['POST'])
@login_required
def add_comment(title):
    recipe = Recipe.query.filter_by(title=title).first_or_404()
    commento = request.form.get('commento')
    if commento:
        new_comment = Comment(recipe_nr=recipe.nr, user_id=current_user.id, commento=commento)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added!', 'success')
    else:
        flash('Comment cannot be empty.', 'warning')
    return redirect(url_for('view_recipe', title=title))

@app.route('/<title>/vote', methods=['POST'])
@login_required
def vote_recipe(title):
    recipe = Recipe.query.filter_by(title=title).first_or_404()
    try:
        voto = int(request.form.get('voto'))
    except (TypeError, ValueError):
        flash('Invalid vote.', 'danger')
        return redirect(url_for('view_recipe', title=title))
    existing_vote = Vote.query.filter_by(recipe_nr=recipe.nr, user_id=current_user.id).first()
    if existing_vote:
        existing_vote.voto = voto
    else:
        new_vote = Vote(recipe_nr=recipe.nr, user_id=current_user.id, voto=voto)
        db.session.add(new_vote)
    db.session.commit()
    flash('Vote recorded!', 'success')
    return redirect(url_for('view_recipe', title=title))

@app.route('/add_to_favorites/<int:recipe_nr>', methods=['POST'])
@login_required
def add_to_favorites(recipe_nr):
    recipe = Recipe.query.get(recipe_nr)
    if not recipe:
        flash('Ricetta non trovata.', 'danger')
        return redirect(url_for('index'))
    existing_favorite = Favorite.query.filter_by(utente_id=current_user.id, recipe_nr=recipe_nr).first()
    if not existing_favorite:
        new_favorite = Favorite(utente_id=current_user.id, recipe_nr=recipe_nr)
        db.session.add(new_favorite)
        db.session.commit()
        flash('Ricetta aggiunta ai preferiti!', 'success')
    else:
        flash('La ricetta è già nei preferiti.', 'info')
    return redirect(url_for('view_recipe', title=recipe.title))

# ========================
# Application Entry Point
# ========================
if __name__ == '__main__':
    print("Creating database tables if they don't exist...")
    with app.app_context():
        db.create_all()
    print("Running Flask application...")
    app.run(debug=True)