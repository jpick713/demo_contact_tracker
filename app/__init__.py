from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_marshmallow import Marshmallow
from flask_bootstrap import Bootstrap
from utils import datetime_converter, date_converter


# Globally accessible libraries
db = SQLAlchemy()
ma = Marshmallow()
r = FlaskRedis()
mail=Mail()
admin=Admin()
login=LoginManager()
migrate=Migrate()
boot=Bootstrap()


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # Initialize Plugins
    db.init_app(app)
    ma.init_app(app)
    r.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    boot.init_app(app)

    with app.app_context():
        # Include our Routes
        from . import routes
        from .auth import auth
        from .main import main
        from .admins import admins
        from .report import report

        # Register Blueprints
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(admins.admins_bp)
        app.register_blueprint(main.main_bp)
        app.register_blueprint(report.report_bp)

        db.create_all()
        
        app.jinja_env.globals.update(datetime_converter=datetime_converter)
        app.jinja_env.globals.update(date_converter=date_converter)

        return app