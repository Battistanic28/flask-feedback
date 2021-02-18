from app import db
from models import User
from flask_bcrypt import Bcrypt

db.drop_all()
db.create_all()

bcrypt = Bcrypt()

user1  = User(username='user1', password=bcrypt.generate_password_hash('user1'), email='user1@gmail.com', first_name='User', last_name='One')
user2  = User(username='user2', password=bcrypt.generate_password_hash('user2'), email='user2@gmail.com', first_name='USER', last_name='TWO')

db.session.add(user1)
db.session.add(user2)
db.session.commit()
