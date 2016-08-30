#!/usr/bin/env python3

import sys
from flask import Flask
from flask_script import Manager, Command
from app import app, db
from app.models import User, Invitation, Connection
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import config
import threading

manager = Manager(app)

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

for module in [__name__,
               "app"
               ]:
    log = logging.getLogger(module)
    log.addHandler(log_handler_mail)
    log.addHandler(log_handler_rotate)
    log.addHandler(log_handler_stdout)


@manager.command
def install():
    db.create_all()


@manager.command
def run():
    app.run()


@manager.command
def start():
    app.run(debug=True)


@manager.command
def testmail():
    from flask_mail import Message
    from app import mail
    msg = Message("Hello",
                  sender="noreply@freedomledger.com",
                  recipients=["mail@xeroc.org"])
    mail.send(msg)


if __name__ == '__main__':
    manager.run()
