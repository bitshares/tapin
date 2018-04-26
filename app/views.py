from bitshares.account import Account
from bitshares import BitShares
import re
from pprint import pprint
import os
import json
import traceback
from flask import render_template, request, session, jsonify, abort
from datetime import datetime
from . import app, models, config
log = app.logger

test_account_name = r"test-faucet.*"


def is_test_account(account_name):
    return re.match(test_account_name, account_name)


def api_error(msg):
    return jsonify({"error": {"base": [msg]}})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/accounts', methods=['POST'], defaults={'referrer': None})
@app.route('/<referrer>/api/v1/accounts', methods=['POST'])
def tapbasic(referrer):
    # test is request has 'account' key
    if not request.json or 'account' not in request.json:
        abort(400)
    account = request.json.get('account', {})

    # make sure all keys are present
    required_files = set(
        (config.get("require_fields", []) or []) +
        ["active_key", "memo_key", "owner_key", "name"]
    )
    for required in required_files:
        if required not in account:
            return api_error("Please provide '{}'".format(required))

    # prevent massive account registration
    if request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    if ip != "127.0.0.1" and models.Accounts.exists(ip):
        return api_error("Only one account per IP")

    # Check if account name is cheap name
    if (not re.search(r"[0-9-]", account["name"]) and
            re.search(r"[aeiouy]", account["name"])):
        return api_error("Only cheap names allowed!")

    # This is not really needed but added to keep API-compatibility with Rails Faucet
    account.update({"id": None})

    bitshares = BitShares(
        config.witness_url,
        nobroadcast=config.nobroadcast,
        keys=[config.wif]
    )

    # See if the account to register already exists
    if not is_test_account(account["name"]):
        try:
            Account(account["name"], bitshares_instance=bitshares)
            return api_error("Account exists")
        except:
            pass

    # Registrar
    registrar = account.get("registrar", config.registrar) or config.registrar
    try:
        registrar = Account(registrar, bitshares_instance=bitshares)
    except:
        return api_error("Unknown registrar: %s" % registrar)

    # Referrer
    referrer = account.get("referrer", config.default_referrer) or config.default_referrer
    try:
        referrer = Account(referrer, bitshares_instance=bitshares)
    except:
        return api_error("Unknown referrer: %s" % referrer)
    referrer_percent = account.get("referrer_percent", config.referrer_percent)

    # Make sure to not broadcast this testing account
    if not bitshares.nobroadcast:
        if is_test_account(account["name"]):
            bitshares.nobroadcast = True
        else:
            bitshares.nobroadcast = False

    if "email" in account and account["email"]:
        try:
            models.Accounts.validate_email(account["email"])
        except Exception as e:
            return api_error(str(e))

    # Create new account
    try:
        tx = bitshares.create_account(
            account["name"],
            registrar=registrar["id"],
            referrer=referrer["id"],
            referrer_percent=referrer_percent,
            owner_key=account["owner_key"],
            active_key=account["active_key"],
            memo_key=account["memo_key"],
            proxy_account=config.get("proxy", None),
            additional_owner_accounts=config.get("additional_owner_accounts", []),
            additional_active_accounts=config.get("additional_active_accounts", []),
            additional_owner_keys=config.get("additional_owner_keys", []),
            additional_active_keys=config.get("additional_active_keys", []),
        )
    except Exception as e:
        log.error(traceback.format_exc())
        return api_error(str(e))

    if not is_test_account(account["name"]):
        models.Accounts(
            account=account["name"],
            full_name=account.get("real_name", None),
            email=account.get("email", None),
            ip=ip
        )

    reply = {"account": {
        "name": account["name"],
        "owner_key": account["owner_key"],
        "active_key": account["active_key"],
        "memo_key": account["memo_key"],
        "referrer": referrer["name"]
    }}

    if is_test_account(account["name"]):
        tx.pop("signatures", None)
        reply.update({"tx": tx})

    return jsonify(reply)
