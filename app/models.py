from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    #posts = db.relationship('Post', backref='author', lazy=True)
    role = db.Column(db.String(50))
    reservations = db.relationship('Reservation', backref='user',lazy=True)

    #roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy ='dynamic'))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(120), nullable=False)
    NationalID = db.Column(db.Integer)
    room = db.Column(db.String(10),nullable=False)
    adults = db.Column(db.String(10),nullable=False)
    children = db.Column(db.String(10),nullable=False)
    checkin = db.Column(db.Date, nullable=False)
    checkout = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10))
    birthdate = db.Column(db.Date)
    date_posted = db.Column(db.DateTime, nullable=False, default= datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"Reservation('{self.name}', '{self.email}', '{self.room}', '{self.adults}', '{self.children}', '{self.checkin}', '{self.checkout}', '{self.date_posted}')"




class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rname = db.Column(db.String(10), unique=True)
    number = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"User('{self.rname}', '{self.number}')"



































""" 
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))


class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default= datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False, unique=True)
    description = db.Column(db.String(200))
    price = db.Column(db.Numeric(2000,2), nullable=False)
    image = db.Column(db.String(20),nullable= False, default='product_default.jpg')

    def __repr__(self):
        return f"Product('{self.name}', '{self.description}', '{self.price}')"
 """