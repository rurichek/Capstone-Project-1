from models import User, Pet, UserPet, db
from app import app

app.app_context().push()

# Create all tables
db.drop_all()
db.create_all()

# Seed Users
users_data = [
    {"first_name": "John", "last_name": "Doe", "username": "john_doe", "password": "password123"},
    {"first_name": "Jane", "last_name": "Smith", "username": "jane_smith", "password": "password456"},
    {"first_name": "Mike", "last_name": "Johnson", "username": "mike_johnson", "password": "password789"},
]

users = [User(**data) for data in users_data]
db.session.add_all(users)
db.session.commit()

# Seed Pets
pets_data = [
    {"api_pet_id": 101, "users": [users[0]]},
    {"api_pet_id": 102, "users": [users[0], users[1]]},
    {"api_pet_id": 103, "users": [users[1]]},
    {"api_pet_id": 104, "users": [users[2]]},
]

pets = [Pet(**data) for data in pets_data]
db.session.add_all(pets)
db.session.commit()

# Seed UserPet (Likes)
user_pet_data = [
    {"user_id": users[0].id, "pet_id": pets[0].id},
    {"user_id": users[0].id, "pet_id": pets[1].id},
    {"user_id": users[1].id, "pet_id": pets[1].id},
    {"user_id": users[1].id, "pet_id": pets[2].id},
    {"user_id": users[2].id, "pet_id": pets[3].id},
]

user_pet_likes = [UserPet(**data) for data in user_pet_data]
db.session.add_all(user_pet_likes)
db.session.commit()
