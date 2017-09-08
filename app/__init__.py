import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import yaml
from flaskext.markdown import Markdown


class Config(dict):
    """ Configuration class loads settings from YAML file
    """
    def __init__(self, *args, **kwargs):
        config = yaml.load(open("config.yml").read())
        super(Config, self).__init__(config)

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Instanciate config
config = Config()

# Instanciate FLASK
app = Flask(__name__)

# Flask settings
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = config.secret_key
app.config['TAP'] = config

# Setup Mail
app.config['MAIL_SERVER'] = config.mail_host.split(":")[0]
app.config['MAIL_PORT'] = int(config.mail_host.split(":")[1])
app.config['MAIL_USERNAME'] = config.mail_user
app.config['MAIL_PASSWORD'] = config.mail_pass
app.config['MAIL_DEFAULT_SENDER'] = config.mail_from
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Setup Storage
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Setup CORS
cors = CORS(app, resources={r".*/api/v1/.*": {"origins": "*"}})

# Markdown for index page
markdown = Markdown(
    app,
    extensions=['meta',
                'tables'
                ],
    safe_mode=True,
    output_format='html4',
)

# Logging
log_handler_mail = SMTPHandler(config.mail_host.split(":"),
                               config.mail_from,
                               config.admins,
                               '[faucet] Error',
                               (config.mail_user,
                                config.mail_pass))
log_handler_mail.setFormatter(logging.Formatter(
    "Message type:       %(levelname)s\n" +
    "Location:           %(pathname)s:%(lineno)d\n" +
    "Module:             %(module)s\n" +
    "Function:           %(funcName)s\n" +
    "Time:               %(asctime)s\n" +
    "\n" +
    "Message:\n" +
    "\n" +
    "%(message)s\n"
))
log_handler_mail.setLevel(logging.WARN)
log_handler_stdout = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler_stdout.setFormatter(formatter)
log_handler_rotate = RotatingFileHandler('faucet.log',
                                         maxBytes=1024 * 1024 * 100,
                                         backupCount=20)
log_handler_rotate.setLevel(logging.CRITICAL)
app.logger.addHandler(log_handler_mail)
app.logger.addHandler(log_handler_rotate)
app.logger.addHandler(log_handler_stdout)

# Load views and models
from . import views, models


# Database
@app.before_first_request
def before_first_request():
    try:
        models.db.create_all()
    except Exception as e:
        app.logger.warning(str(e))
