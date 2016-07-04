import sys
from flask import Flask
from flask_script import Manager, Command
from flask_migrate import Migrate, MigrateCommand
from app import app, db
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import config

manager = Manager(app)

log_handler_mail = SMTPHandler(config.mail_host,
                               config.mail_from,
                               config.admins,
                               '[Tap] Error',
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
log_handler_stdout = logging.StreamHandler(sys.stdout)
log_handler_rotate = RotatingFileHandler(
    '%s.log' % __file__,
    maxBytes=1024 * 1024 * 100,
    backupCount=20
)

log = logging.getLogger(__name__)
log_handler_mail.setLevel(logging.ERROR)
log_handler_rotate.setLevel(logging.INFO)

log.addHandler(log_handler_rotate)
log.addHandler(log_handler_stdout)
log.addHandler(log_handler_mail)

cors = logging.getLogger('flask_cors')
cors.setLevel(logging.INFO)
cors.addHandler(log_handler_stdout)


@manager.command
def install():
    db.create_all()


@manager.command
def run():
    app.run()


@manager.command
def start():
    app.run(debug=True)


migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
