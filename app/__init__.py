import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.config import DevelopmentConfig

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'admin.login'


def create_app(config_class=DevelopmentConfig):
    current_path = os.path.abspath(__file__)
    src_dir = os.path.dirname(current_path)
    parent_dir = os.path.dirname(src_dir)
    app = Flask(__name__,
                template_folder=parent_dir + "/" + config_class.TEMPLATE_FOLDER,
                static_folder=parent_dir + "/" + config_class.STATIC_FOLDER)
    app.config.from_object(config_class)

    login_manager.init_app(app)

    CORS(app)

    db.init_app(app)

    from app.views.pages import api, static_pages
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(static_pages)

    from app.views.admin import admins
    app.register_blueprint(admins)

    return app
