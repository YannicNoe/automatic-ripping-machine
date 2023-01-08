"""Main arm ui file"""
import sys  # noqa: F401
import os  # noqa: F401
from getpass import getpass  # noqa: F401
from logging.config import dictConfig
from flask import Flask, logging, current_app  # noqa: F401
from flask.logging import default_handler  # noqa: F401
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf import CSRFProtect

from flask_login import LoginManager
import bcrypt  # noqa: F401
import arm.config.config as cfg

sqlitefile = 'sqlite:///' + cfg.arm_config['DBFILE']

# Setup logging, but because of werkzeug issues, we need to set up that later down file
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s ARM: %(module)s.%(funcName)s %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        "console": {"class": "logging.StreamHandler", "level": "INFO"},
        "null": {"class": "logging.NullHandler"},
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    },
})

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
CORS(app, resources={r"/*": {"origins": "*", "send_wildcard": "False"}})

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = sqlitefile
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# We should really generate a key for each system
app.config['SECRET_KEY'] = "Big secret key"  # make this random!
app.config['LOGIN_DISABLED'] = cfg.arm_config['DISABLE_LOGIN']
# Set debug pin as it is hidden normally
os.environ["WERKZEUG_DEBUG_PIN"] = "12345"  # make this random!
app.logger.debug("Debugging pin: " + os.environ["WERKZEUG_DEBUG_PIN"])

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Register route blueprints
# loaded post database decleration to avoid circular loops
from arm.ui.settings.settings import route_settings # noqa: E402,F811
app.register_blueprint(route_settings)

# Remove GET/page loads from logging
import logging  # noqa: E402,F811
logging.getLogger('werkzeug').setLevel(logging.ERROR)
