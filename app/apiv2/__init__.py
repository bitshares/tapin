import re
import traceback
from flask import request, jsonify, Blueprint
from bitshares.account import Account
from bitshares import BitShares
from .. import app, models, config
log = app.logger

apiv2 = Blueprint(
    "apiv2",
    __name__,
)


def api_error(msg):
    return jsonify({"error": {"base": [msg]}})


@apiv2.route(
    '/api/v2/create/<name>/<owner>/<active>/<memo>',
    methods=['GET'], defaults={'referrer': None})
def tapv2(name, owner, active, memo, referrer):
    # prevent massive account registration
    if request.remote_addr != "127.0.0.1" and \
            models.Accounts.exists(request.remote_addr):
        return api_error("Only one account per IP")

    # Check if account name is cheap name
    if (not re.search(r"[0-9-]", name) and
            re.search(r"[aeiouy]", name)):
        return api_error("Only cheap names allowed!")

    bitshares = BitShares(
        config.witness_url,
        nobroadcast=config.nobroadcast,
        keys=[config.wif]
    )

    try:
        Account(name, bitshares_instance=bitshares)
        return api_error("Account exists")
    except:
        pass

    # Registrar
    registrar = config.registrar
    try:
        registrar = Account(registrar, bitshares_instance=bitshares)
    except:
        return api_error("Unknown registrar: %s" % registrar)

    # Referrer
    if not referrer:
        referrer = config.default_referrer
    try:
        referrer = Account(referrer, bitshares_instance=bitshares)
    except:
        return api_error("Unknown referrer: %s" % referrer)
    referrer_percent = config.referrer_percent

    # Create new account
    try:
        bitshares.create_account(
            name,
            registrar=registrar["id"],
            referrer=referrer["id"],
            referrer_percent=referrer_percent,
            owner_key=owner,
            active_key=active,
            memo_key=memo,
            proxy_account=config.get("proxy", None),
            additional_owner_accounts=config.get(
                "additional_owner_accounts", []),
            additional_active_accounts=config.get(
                "additional_active_accounts", []),
            additional_owner_keys=config.get(
                "additional_owner_keys", []),
            additional_active_keys=config.get(
                "additional_active_keys", []),
        )
    except Exception as e:
        log.error(traceback.format_exc())
        return api_error(str(e))

    models.Accounts(name, request.remote_addr)

    return jsonify({
        "status": "Account created",
        "account": {
            "name": name,
            "owner_key": owner,
            "active_key": active,
            "memo_key": memo,
        }})
