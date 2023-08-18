import requests, os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for         
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import RegisterForm, LoginForm
from models import db, connect_db, User, Pet, UserPet
from werkzeug.exceptions import Unauthorized
from keys import client_id, client_secret


app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///pet_finder'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

app.app_context().push()

connect_db(app)

# client_id = 'XGy5nVoH6i8sW3rwPSCUkVL5rga5Tu1ILH2BLxRmibR7xRxXPI'
# client_secret = 'u7XaxsDc4B4BGmDY4TjNXZSxtMwnigeVtjTBt9kA'

def get_petfinder_access_token(client_id, client_secret):
    url = 'https://api.petfinder.com/v2/oauth2/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return None

access_token = get_petfinder_access_token(client_id, client_secret)
if access_token:
    print("Acccess Token:", access_token)
else:
    print("Failed to get Access Token.")

headers={
        'Authorization': f'Bearer {access_token}' 
        }

res = requests.get(
    'https://api.petfinder.com/v2/animals', 
    headers=headers
)
data = res.json()
# print(data['animals'][0]['contact'])

# for result in data['animals']:
#     print(result['id'])
#     print(result['name'])
#     print(result['species'])
#     print('---')
def get_breed():
    url = 'https://api.petfinder.com/v2/types/dog/breeds'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()['breeds']
    else:
        return None


# if breeds:
#     print('Breeds have been successfully obtained')
# else:
#     print("Failed to get breeds")


@app.route("/")
def root():
    """Homepage: redirect to /pets."""

    return redirect("/location")

@app.route("/pets")
def show_all_pets():
    """Return a list of pets."""

    # animal_type = session['animal_type']

    pets = Pet.query.all()
    # return render_template("pets.html", pets=pets)
    return redirect(url_for('load_pets'))

@app.route("/location")
def get_location():


    return render_template("location.html")

##########################################################################################

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""

    if "username" in session:
        return redirect("/")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, first_name, last_name)

        db.session.commit()
        session['username'] = user.username

        return redirect("/")

    else:
        return render_template("register.html", form=form)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    if "username" in session:
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)  # <User> or False
        if user:
            session['username'] = user.username
            return redirect("/")
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template("login.html", form=form)

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.pop('username')

    return redirect("/login")

##########################################################################################
 
@app.route('/search', methods=['GET'])
def search():
    #This section incorporated from the favorites to display/fetch
    # likes on page load
    username = session.get("username")
    if not username:
        flash("Username not found in session")
        return redirect("/login")
    else:
        user = User.query.filter_by(username=username).first()
        if user:
            liked_pets = user.pets
        else:
            flash("Username not found in the database.")
            return redirect('/register')

    likes = [pet.api_pet_id for pet in liked_pets]
############################End fetching##########################


# Extract the selected options from the query string
    session['animal_type'] = request.args.get('animal_type')
    session['age'] = request.args.get('age')
    session['gender'] = request.args.get('gender')
    if request.args.get('location') and request.args.get('location').strip() != "":
        session['location'] = request.args.get('location')
    else:
        flash("Please enter the location in a form 'City, State' or 'Zip Code'")
        return render_template('location.html')
    session['distance'] = request.args.get('distance')
    session['breed'] = request.args.get('breed')

    # Build the API request using the values from session
    params = {
        'type': session['animal_type'],
        'age': session['age'],
        'gender': session['gender'],
        'location': session['location'],
        'distance': session['distance'] or 10,
        'breed': session['breed']
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get('https://api.petfinder.com/v2/animals', params=params, headers=headers)

    # Parse the API response
    data = response.json()
    animals = data["animals"]

    breeds = get_breed()

    location = session.get('location')

    # Render the search results
    return render_template('pets.html', animals=animals, breeds=breeds, likes=likes, location=location)

# @app.route('/location', methods=['GET', 'POST'])
# def get_location():
#     """Sho form asking for location of the user"""

# form = LoginForm()

# if form.validate_on_submit():
#     username = form.username.data
#     password = form.password.data

#     user = User.authenticate(username, password)  # <User> or False
#     if user:
#         session['username'] = user.username
#         return redirect("/")
#     else:
#         form.username.errors = ["Invalid username/password."]
#         return render_template("login.html", form=form)

#     return render_template('location.html')

@app.route('/details')
def details():

    pet_id = request.args.get('petId')

    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.get(f'https://api.petfinder.com/v2/animals/{pet_id}', headers=headers)

    data = response.json()

    animal = data["animal"]

    return render_template('details.html', pet_id=pet_id, animal=animal)


@app.route('/saved')
def saved():

    #This section incorporated from the favorites to display/fetch
    # likes on page load
    username = session.get("username")
    if not username:
        flash("Username not found in session")
        return redirect("/login")
    else:
        user = User.query.filter_by(username=username).first()
        if user:
            liked_pets = user.pets
        else:
            flash("Username not found in the database.")
            return redirect('/register')

    likes = [pet.api_pet_id for pet in liked_pets]
############################End fetching##########################

    user = User.query.filter_by(username=session['username']).first()

    favorites = user.pets

    favorites_list = []

    user = User.query.filter_by(username = session['username']).first()

    for pet in favorites:

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(f'https://api.petfinder.com/v2/animals/{pet.api_pet_id}', headers=headers)

        data = response.json()

        animal = data["animal"]

        favorites_list.append(animal)


    return render_template('favorites.html', favorites=favorites, favorites_list=favorites_list, likes=likes, user=user)


@app.route('/favorites', methods=['GET', 'POST'])
def add_like():


    #here we are assigning some variables such as user and liked pets 
    #and we are adding error message if the user is not logged in
    #or the user is not found in the database. 
    username = session.get("username")
    if not username:
        flash("Username not found in session")
        return redirect("/login")
    else:
        user = User.query.filter_by(username=username).first()
        if user:
            liked_pets = user.pets
        else:
            flash("Username not found in the database.")
            return redirect('/register')

    #extracting api ids from pets
    likes = [pet.api_pet_id for pet in liked_pets]

    # for like in likes: 

    # we need to add the liked pet to Pet database
    pet_id_str = request.args.get('petId')
    if pet_id_str and pet_id_str.isdigit():
        pet_id = int(pet_id_str)
    else:
        flash("Invalid pet ID provided")
        return redirect('/pets')

    if pet_id in likes:
        # return render_template('pets.html')
        pet = Pet.query.filter_by(api_pet_id = pet_id).first()

        db.session.delete(pet)
        db.session.commit()

    else:
        added_pet = Pet(api_pet_id=pet_id)

        db.session.add(added_pet)
        db.session.commit()

        #here we are adding the liked pet to the association table
        user = User.query.filter_by(username = session['username']).first()

        pet = Pet.query.filter_by(api_pet_id = pet_id).first()

        association = UserPet(user_id=user.id, pet_id=pet.id)

        db.session.add(association)
        db.session.commit()


    # return render_template('pets.html', likes=likes)
    return redirect(url_for('load_pets'))
    # return render_template('pets.html', likes=likes)

@app.route('/load_pets')
def load_pets():

    #This section incorporated from the favorites to display/fetch
    # likes on page load
    username = session.get("username")
    if not username:
        flash("Username not found in session")
        return redirect("/login")
    else:
        user = User.query.filter_by(username=username).first()
        if user:
            liked_pets = user.pets
        else:
            flash("Username not found in the database.")
            return redirect('/register')

    likes = [pet.api_pet_id for pet in liked_pets]
############################End fetching##########################

    # Build the API request using the values from session
    params = {
        'type': session['animal_type'],
        'age': session['age'],
        'gender': session['gender'],
        'location': session['location'],
        'distance': session['distance'] or 10,
        'breed': session['breed']
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get('https://api.petfinder.com/v2/animals', params=params, headers=headers)

    # Parse the API response
    data = response.json()
    animals = data["animals"]

    location = session.get('location')


    return render_template('pets.html', animals=animals, likes=likes, location=location)

@app.route('/favorites2', methods=['GET', 'POST'])
def add_like2():


    #here we are assigning some variables such as user and liked pets 
    #and we are adding error message if the user is not logged in
    #or the user is not found in the database. 
    username = session.get("username")
    if not username:
        flash("Username not found in session")
        return redirect("/login")
    else:
        user = User.query.filter_by(username=username).first()
        if user:
            liked_pets = user.pets
        else:
            flash("Username not found in the database.")
            return redirect('/register')

    #extracting api ids from pets
    likes = [pet.api_pet_id for pet in liked_pets]

    # for like in likes: 


    # we need to add the liked pet to Pet database
    pet_id_str = request.args.get('petId')
    if pet_id_str and pet_id_str.isdigit():
        pet_id = int(pet_id_str)
    else:
        flash("Invalid pet ID provided")
        print(pet_id)
        return redirect('/pets')

    print('******liked pet*****')
    print(pet_id)
    print(type(pet_id))

    if pet_id in likes:
        print('pet id found')
        # return render_template('pets.html')
        pet = Pet.query.filter_by(api_pet_id = pet_id).first()

        db.session.delete(pet)
        db.session.commit()

    else:
        added_pet = Pet(api_pet_id=pet_id)

        db.session.add(added_pet)
        db.session.commit()

        #here we are adding the liked pet to the association table
        user = User.query.filter_by(username = session['username']).first()

        pet = Pet.query.filter_by(api_pet_id = pet_id).first()

        association = UserPet(user_id=user.id, pet_id=pet.id)

        db.session.add(association)
        db.session.commit()


    # return render_template('pets.html', likes=likes)
    # return render_template('favorites.html', pet_id=pet_id, user=user, likes=likes)
    return redirect("/saved")





