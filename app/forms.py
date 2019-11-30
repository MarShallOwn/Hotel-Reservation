from datetime import datetime
from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Reservation, Room



class RegistrationForm(FlaskForm):
    username = StringField('Username',
     validators=[DataRequired(), Length(min=2, max=20) ])
    
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password',validators=[DataRequired()])
    
    confirm_password = PasswordField('Confirm Password', 
     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That Username is taken. Please choose a different one.')

    def validate_email(self, email):
        
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That Email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password',validators=[DataRequired()])

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):

    username = StringField('Username',
     validators=[DataRequired(), Length(min=2, max=20) ])
    
    email = StringField('Email', validators=[DataRequired(), Email()])

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'jfif'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That Username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('That Email is taken. Please choose a different one.')


class ReservationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    NationalID = StringField('National ID')
    room = SelectField('Room Type')
    adults = SelectField('Adults', choices=[ ('one', 1), ('two', 2), ('three', 3) ])
    children = SelectField('Children', choices=[ ('zero', 0), ('one', 1), ('two', 2) ])
    checkin = DateField('Check In',format='%Y-%m-%d', validators=[DataRequired()])
    checkout = DateField('Check Out', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Check In')
                

    def validate_room(self, room):
            room = Room.query.filter_by(rname = room.data).first()
            if room.number == 0:
                raise ValidationError('That Room is already taken. Please choose a different one.')

    def validate_checkout(self, checkout):
            if self.checkin.data > checkout.data:
                raise ValidationError('Checkout should be after checkin date')

class ReservationLoginForm(FlaskForm):
    ReservationID = StringField('Reservation ID', validators=[DataRequired(), Length(min=10, max=10) ])
    submit = SubmitField('Check Reservation')







""" 
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = StringField('Description')
    price = StringField('Price', validators=[DataRequired()])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'jfif'])])
    submit = SubmitField('Submit')

    def validate_name(self, name):
            product = Product.query.filter_by(name = name.data).first()
            if product and str(request.url_rule) != '/product/<int:product_id>/update':
                raise ValidationError('That name is taken. Please choose a different one.') """