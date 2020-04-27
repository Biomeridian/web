import os
from flask import Flask, request, current_app
from flask.json import JSONEncoder
from datetime import date
from flask_behind_proxy import FlaskBehindProxy
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_session import Session
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_principal import Principal, identity_loaded
import flask_excel as excel
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'user_views.login'
login.login_message = 'Please log in to access this page.'
login.session_protection = "strong"
sess = Session()
bootstrap = Bootstrap()
admin = Admin()
principal = Principal() 


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        return super().default(o)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # initialize plugins
    proxied_app = FlaskBehindProxy(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    sess.init_app(app)
    bootstrap.init_app(app)
    admin.init_app(app)
    principal.init_app(app)
    excel.init_excel(app)

    # connect listener for identity loaded signal
    from app.user.roles import on_identity_loaded
    identity_loaded.connect_via(app)(on_identity_loaded)

    # register blueprints
    from app.user.google import bp as google_bp
    app.register_blueprint(google_bp, url_prefix='/login')

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.projects import bp as projects_bp
    app.register_blueprint(projects_bp, url_prefix='/projects')

    from app.audio import bp as audio_bp
    app.register_blueprint(audio_bp)

    from app.clusters import bp as clusters_bp
    app.register_blueprint(clusters_bp)

    from app.labels import bp as labels_bp
    app.register_blueprint(labels_bp)

    from app.ml import bp as ml_bp
    app.register_blueprint(ml_bp, url_prefix='/ml')

    # custom overrides
    app.json_encoder = CustomJSONEncoder

    return app

from app import models

