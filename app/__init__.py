#!/use/bin/env python3

import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_mail import Mail
import config
from flask_cors import CORS
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = config.secret_key
app.config['TAP'] = config
sess = Session()

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['MAIL_SERVER'] = config.mail_host.split(":")[0]
app.config['MAIL_PORT'] = int(config.mail_host.split(":")[1])
app.config['MAIL_USERNAME'] = config.mail_user
app.config['MAIL_PASSWORD'] = config.mail_pass
app.config['MAIL_DEFAULT_SENDER'] = config.mail_from
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from . import views, models

# Logging
log_handler_mail = SMTPHandler(config.mail_host.split(":"),
                               config.mail_from,
                               config.admins,
                               '[Faucet] Error',
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
log_handler_mail.setLevel(logging.ERROR)
log_handler_stdout = logging.StreamHandler(sys.stdout)
# log_handler_stdout.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler_stdout.setFormatter(formatter)
log_handler_rotate = RotatingFileHandler('faucet.log',
                                         maxBytes=1024 * 1024 * 100,
                                         backupCount=20)
log_handler_rotate.setLevel(logging.CRITICAL)

cors = logging.getLogger('flask_cors')
cors.setLevel(logging.INFO)
cors.addHandler(log_handler_stdout)

log = logging.getLogger(__name__)
log.addHandler(log_handler_mail)
log.addHandler(log_handler_rotate)
log.addHandler(log_handler_stdout)


# Database
@app.before_first_request
def before_first_request():
    try:
        models.db.create_all()
    except Exception as e:
        app.logger.warning(str(e))
