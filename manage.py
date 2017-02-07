#!/usr/bin/env python3

import sys
from flask import Flask
from flask_script import Manager, Command
from app import app, db
from app import config
import threading

manager = Manager(app)


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
def donations(start=None, end=None):
    import worker_donations
    worker_donations.run(start, end)


@manager.command
def testmail():
    from flask_mail import Message
    from app import mail
    msg = Message("Hello",
                  sender=config.mail_from,
                  recipients=config.admins)
    mail.send(msg)


if __name__ == '__main__':
    manager.run()
