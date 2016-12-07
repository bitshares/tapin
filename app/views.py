import re
from pprint import pprint
import json
import os
from flask import render_template, request, session, jsonify, abort
from . import app, models
from datetime import datetime
import traceback
from . import config
from . import bitshares
from graphenebase.account import PasswordKey
log = app.logger


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
    if any([key not in account
            for key in ["active_key", "memo_key", "owner_key", "name"]]):
        abort(400)

    # prevent massive account registration
    if models.Accounts.exists(request.remote_addr):
        return api_error("Only one account per IP")

    # Check if account name is cheap name
    if (not re.search(r"[0-9-]", account["name"]) and
            re.search(r"[aeiouy]", account["name"])):
        return api_error("Only cheap names allowed!")

    # This is not really needed but added to keep API-compatibility with Rails Faucet
    account.update({"id": None})

    bts = bitshares.BitShares(nobroadcast=config.nobroadcast)

    if bts.check_account_exists(account["name"]):
        return api_error("Account exists")

    if referrer:
        ref = referrer
    else:
        ref = account.get("referrer", None)

    if ref and not bts.check_account_exists(ref):
        return api_error("Referrer does not exist!")

    account = {
        "name": account["name"],
        "owner_key": account["owner_key"],
        "active_key": account["active_key"],
        "memo_key": account["memo_key"],
        "referrer": ref
    }

    # Create new account
    try:
        bts.create_account(account)
    except Exception as e:
        log.error(traceback.format_exc())
        return api_error(str(e))

    models.Accounts(account["name"], request.remote_addr)

    if bts.get_balance() < config.balance_mailthreshold:
        log.warning(
            "The faucet's balances is below {}".format(
                config.balance_mailthreshold
            ),
        )

    return jsonify({"account": account})
