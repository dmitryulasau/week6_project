
from flask import render_template, request, url_for, flash, redirect, make_response
from app import app

from flask import render_template, flash, redirect
from .forms import FindPokemon, LoginForm
import requests

from flask_login import current_user, login_user, logout_user, login_required
from app.models import Pokemon, User

from app import db
from app.forms import RegistrationForm

from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    
    form = FindPokemon()

    if request.method =='POST':
        
        name = request.form.get('name')
        url = f"https://pokeapi.co/api/v2/pokemon/{name}"
        response = requests.get(url)

        if not response.ok:
            error_message = "Please enter a valid name or number (1-905)"
            return render_template('index.html.j2', error=error_message, form=form)
        if not response.json():
            error_message = "We don't have this Pokemon's name"
            return render_template('index.html.j2', error=error_message, form=form)    
        data = response.json()
        
        pokemon_info = []
        
        pokemon_dict = {}
   
        pokemon_dict = {
            'name': data["species"]['name'],
            "pokemon_id_original": data["id"],
            'ability': data['abilities'][0]['ability']['name'],
            'defense': data['stats'][2]['base_stat'],
            'attack': data['stats'][1]['base_stat'],
            'hp': data['stats'][0]['base_stat'],
            'image': data['sprites']['other']['official-artwork']['front_default'],
            'gif': data['sprites']['versions']['generation-v']['black-white']['animated']['front_shiny']
        }

        
        pokemon_info.append(pokemon_dict)

        new_poke = Pokemon()
        new_poke.poke_to_db(pokemon_dict)
        new_poke.save()

        return render_template('index.html.j2', info=pokemon_info, form=form, user=user, pokemon_data=pokemon_dict)

    return render_template('index.html.j2', title='Home', user=user, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html.j2', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data, password=generate_password_hash(form.password.data, method='sha256'))
        
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful! Now you may login')
        return redirect(url_for('login'))
    return render_template('register.html.j2', title='Register', form=form)


@app.route('/user/<email>')
@login_required
def user(email):
    user = User.query.filter_by(email=email).first_or_404()
   
    return render_template('user.html.j2', user=user)



@app.route('/show_users')
def show_users():
    users=User.query.filter(User.id != current_user.id).all()
    return render_template('show_users.html.j2', users=users)

@app.delete("/user/<id>")
def delete_user(id):
    """Delete a user"""
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return make_response("User vanished.", 200)

@app.delete("/pokemon/<id>")
def delete_pokemon(id):
    """Delete a pokemon"""
    Pokemon.query.filter_by(id=id).delete()
    db.session.commit()
    return make_response("Pokemon vanished.", 200)
###############################################################
@app.route("/catch/<string:name>")
@login_required
def catch(name):
    poke = Pokemon().query.filter_by(name=name).first()
    print(poke)
    if not current_user.check_user_has_poke(poke) and current_user.owning.count() < 5:
        current_user.catch_poke(poke)
        flash(f"{poke.name.title()} CATCHED!", "success")
        if current_user.owning.count() == 5:
            return redirect(url_for("collection"))
        return redirect(url_for("index"))
    elif current_user.check_user_has_poke(poke):
        flash("This pokemon is already in your collection", "danger")
        return redirect(url_for("index"))
    elif current_user.owning.count() == 5:
        flash("Team is full!", "danger")
        return redirect(url_for("collection"))
    flash("ERROR!!!")
    return redirect(url_for("index"))

@app.route("/collection")
@login_required
def collection():
    if current_user.owning.count() > 0:
        return render_template("collection.html.j2", pokemon=current_user.owning, user=current_user)
    flash("Chatch pokemons to see the collection", "danger")
    return redirect(url_for("index"))
############################################################
@app.route("/release/<string:name>")
@login_required
def release(name):
    poke = Pokemon().query.filter_by(name=name).first()
    if current_user.check_user_has_poke(poke):
        current_user.release_poke(poke)
        flash(f"Bye, bye {poke.name.upper()}!", "success")
        return redirect(request.referrer or url_for("collection"))
   
    return redirect(url_for("index"))