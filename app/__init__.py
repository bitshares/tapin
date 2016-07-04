#!/use/bin/env python3

import os
from flask import Flask, redirect, url_for, session, current_app
from flask_assets import Environment
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_mail import Mail
from datetime import date
from grapheneapi import GrapheneClient
import config
from flask_cors import CORS, cross_origin

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


@app.before_first_request
def before_first_request():
    try:
        models.db.create_all()
    except Exception as e:
        app.logger.warning(str(e))
