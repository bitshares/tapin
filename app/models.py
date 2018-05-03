import datetime

from validate_email import validate_email

from . import db
from . import config


class Accounts(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(255), unique=True)
    ip = db.Column(db.String(100))
    created = db.Column(db.DateTime())

    full_name = db.Column(db.String(255))
    email = db.Column(db.String(255))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise Exception("Used non-existing attribute %s" % key)

        self.created = datetime.datetime.now()

        if self.email:
            self.validate_email(self.email)

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def validate_email(email):
        if not validate_email(email):
            raise ValueError("Invalid Email Address")

    @staticmethod
    def allowedAge():
        return (
            datetime.datetime.now() -
            datetime.timedelta(seconds=config.minIPAge))

    @staticmethod
    def getIps():
        ips = []
        for i in Accounts.query.options().all():
            if (
                config.get("restrict_ip", True) and
                Accounts.allowedAge() < i.created
            ):
                ips.append(i.ip)
        return ips

    @staticmethod
    def exists(address):
        return (
            config.get("restrict_ip", True) and
            bool(Accounts.query.filter(
                (Accounts.ip == address),
                (Accounts.created > Accounts.allowedAge())
            ).first())
        )
