from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Pro přístup na tuto stránku se prosím přihlaste.'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        db.init_app(app)
        bcrypt.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)

    from flask_app.auth.routes import auth
    from flask_app.errors.handlers import errors
    from flask_app.reservations.routes import reservations
    from flask_app.terms.routes import terms
    from flask_app.users.routes import users

    app.register_blueprint(auth)
    app.register_blueprint(errors)
    app.register_blueprint(reservations)
    app.register_blueprint(terms)
    app.register_blueprint(users)

    return app
