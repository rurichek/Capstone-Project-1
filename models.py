"""SQLAlchemy models for pet_finder."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False,
        unique=False,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    # start_register
    @classmethod
    def register(cls, username, password, first_name, last_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        user = cls(
            username=username,
            password=hashed_utf8,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

    def __repr__(self):
        return f"<ID: {self.id}, First Name: {self.first_name}, Last Name: {self.last_name}, Username: {self.username}>"

class Pet(db.Model):
    """Favorited pets"""

    __tablename__ = 'pets'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    api_pet_id = db.Column(
        db.Integer,
        # autoincrement=True,
        nullable=False,
        unique=False,
    )

    # name = db.Column(
    #     db.Integer,
    #     autoincrement=True,
    #     nullable=False,
    #     unique=False,
    # )

    # organization_id = db.Column(
    #     db.Integer,
    #     # autoincrement=True,
    #     nullable=False,
    #     unique=False,
    # )

    users = db.relationship('User', secondary='pets_users', backref='pets')

    def __repr__(self):
        return f"<ID: {self.id} API ID: {self.api_pet_id}>"

class UserPet(db.Model):
    """Association table to connect users with their liked pet"""

    __tablename__ = 'pets_users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        # primary_key=True,
    )

    pet_id = db.Column(
        db.Integer,
        db.ForeignKey('pets.id', ondelete="cascade"),
        # primary_key=True,
    )

    # user = db.relationship('User', backref=db.backref('liked_pets', lazy=True))
    # pet = db.relationship('Pet', backref=db.backref('liking_users', lazy=True))