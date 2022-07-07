from flask import Flask
from flask_bcrypt import Bcrypt
import secrets
from os import path
from datetime import timedelta


def create_app():
    app = Flask(__name__)
    # create the secret_key_hash
    secret_key = secrets.token_hex(16)
    bcrypt = Bcrypt(app)
    secret_key_hash = bcrypt.generate_password_hash(secret_key)
    app.config['SECRET_KEY'] = secret_key_hash
    app.permanent_session_lifetime = timedelta(minutes=10)
    
    from .views import views
    from .auth import auth
    # create the Views Blueprint
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    

    
    return app
