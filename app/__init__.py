from dotenv import load_dotenv
load_dotenv()
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from secrets import token_bytes
from base64 import b64encode
basedir = os.path.abspath(os.path.dirname(__file__))

secretKey = os.environ.get("SECRET_KEY") if os.environ.get("SECRET_KEY") is not None else b64encode(token_bytes(250)).decode("ascii")

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secretKey
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'hotel-reservation.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from app import routes