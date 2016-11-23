import os
import json
GRAPHENE_1_PERCENT = (10000 / 100)

# Random keys
secret_key = os.environ["secret_key"]

# Safety mode
nobroadcast = os.environ["nobroadcast"].lower() in ["true", "yes", "y"]

# Mailing
mail_host = os.environ["mail_host"]
mail_user = os.environ["mail_user"]
mail_pass = os.environ["mail_pass"]
mail_from = os.environ["mail_from"]
admins    = json.loads(os.environ["admins"])

# Ip Delay - How long does an IP need to wait to register a new account?
minIPAge = int(os.environ["minIPAge"])


# BitShares config
class BitSharesConfig():
    witness_url = os.environ["witness_url"]
    prefix      = os.environ["prefix"] if "prefix" in os.environ["prefix"] else "BTS"


# Faucet settings
registrar        = os.environ["registrar"]
default_referrer = os.environ["default_referrer"]
referrer_percent = int(os.environ["referrer_percent"]) * GRAPHENE_1_PERCENT
wif              = os.environ["wif"]
