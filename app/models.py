from sqlalchemy.sql import func
from sqlalchemy.orm import load_only
from . import db
import datetime
import json
import os
from . import config


class Accounts(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(255), unique=True)
    ip = db.Column(db.String(100))
    created = db.Column(db.DateTime())

    def __init__(self, account, ip):
        self.account = account
        self.ip = ip
        self.created = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getIps():
        ips = []
        for i in Accounts.query.options().all():
            allowedAge = datetime.datetime.now() - datetime.timedelta(seconds=config.minIPAge)
            if allowedAge < i.created:
                ips.append(i.ip)
        return ips

    @staticmethod
    def exists(address):
        allowedAge = datetime.datetime.now() - datetime.timedelta(seconds=config.minIPAge)
        return Accounts.query.filter(
            (Accounts.ip == address),
            (Accounts.created > allowedAge)
        ).first()
