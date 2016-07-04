from pprint import pprint
import json
import os
from flask import render_template, request, session, jsonify, abort
from . import app, models
from datetime import datetime
import traceback
import config
from . import bitshares
from graphenebase.account import PasswordKey


def api_error(msg):
    return jsonify({"error": {"base": [msg]}})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/accounts', methods=['POST'])
def tapbasic():

    if not request.json or 'account' not in request.json:
        abort(400)
    account = request.json.get('account', {})

    for key in ["active_key", "memo_key", "owner_key", "name"]:
        if key not in account:
            abort(400)

    if request.remote_addr in models.Accounts.getIps():
        return api_error("Only one account per IP")

    # This is not really needed but added to keep API-compatibility with Rails Faucet
    account.update({"id": None})

    bts = bitshares.BitShares(nobroadcast=config.nobroadcast)

    if bts.check_account_exists(account["name"]):
        return api_error("Account exists")

    account = {
        "name": account["name"],
        "owner_key": account["owner_key"],
        "active_key": account["active_key"],
        "memo_key": account["memo_key"],
        "referrer": account.get("referrer", None)
    }

    # Create new account
    try:
        bts.create_account(account)
    except Exception as e:
        print(traceback.format_exc())
        return api_error(str(e))

    models.Accounts(account["name"], request.remote_addr)

    return jsonify({"account": account})
