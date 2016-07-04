import os
import json
GRAPHENE_1_PERCENT = (10000 / 100)

# Random keys
secret_key = "RANDOM-STRING"

# Safety mode
nobroadcast = True

# Mailing
mail_host = "SERVER:PORT"
mail_user = "user"
mail_pass = "password"
mail_from = "noreply@faucet.org"
admins    = ["adminA@example.com", "adminB@example.com"]

# Ip Delay - How long does an IP need to wait to register a new account?
minIPAge = 60 * 5  # 5 min


# BitShares config
class BitSharesConfig():
    witness_url   = "wss://bitshares.openledger.info/ws"
    # witness_url   = "wss://testnet.bitshares.eu/ws"
    # prefix        = "TEST"


# Faucet settings
registrar        = "xeroc",
default_referrer = "xeroc",
referrer_percent = 50 * GRAPHENE_1_PERCENT,
wif              = "<active-private-key-of-registrar>",
