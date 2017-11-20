#!/usr/bin/env python3

import click


default_config = {
    "secret_key": "RANDOM-STRING",
    "nobroadcast": True,
    "mail_host": "SERVER:589",
    "mail_user": "user",
    "mail_pass": "password",
    "mail_from": "noreply@faucet.org",
    "admins": [
        "adminA@example.com",
        "adminB@example.com"
    ],
    "minIPAge": 300,
    "witness_url": "wss://node.bitshares.eu",
    "registrar": "faucet",
    "default_referrer": "xeroc",
    "referrer_percent": 50,
    "wif": "5KAniAqT1y4orQQ7KopKJ85QQXbVU92jbpV6KGGy5b396LpLYLM",
    "balance_mailthreshold": 500,
    "core_asset": "BTS"
}


@click.group()
def main():
    pass


@main.command()
def install():
    """ Setup default database """
    from app import db
    db.create_all()


@main.command()
def run():
    """ Run the faucet in operational mode """
    from app.web import app
    app.run()


@main.command()
def debug():
    """ Start debugging mode """
    from app.web import app
    app.run(debug=True)


@main.command()
def create(example="config"):
    """ Create a default configuration file """
    import yaml
    config_file = "config.yml"
    with open(config_file, "w") as fd:
        dump = yaml.dump(
            default_config,
            default_flow_style = False)
        fd.write( dump )
    print("Config file created: %s" % config_file)


@main.command()
def gift(start=None, end=None):
    """ Daemon that sends out gifts on new registrations """
    import registration_gift
    registration_gift.run(start, end)


@main.command()
def testmail():
    """ Send a testmail """
    from flask_mail import Message
    from app import mail, config
    msg = Message("Hello",
                  sender=config["mail_from"],
                  recipients=config["admins"])
    mail.send(msg)


if __name__ == '__main__':
    main()
