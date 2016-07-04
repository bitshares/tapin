from pprint import pprint
from grapheneapi.grapheneclient import GrapheneClient
from graphenebase import transactions
import config


class APIUnavailable(Exception):
    pass


class BroadcastingError(Exception):
    pass


class MissingKeyError(Exception):
    pass


class MissingRegistrarError(Exception):
    pass


class MissingPublicKeys(Exception):
    pass


class BitShares():

    def __init__(self, *args, **kwargs):
        self.nobroadcast = kwargs.pop("nobroadcast", False)

    def connect(self, *args, **kwargs):
        try:
            self.rpc = GrapheneClient(config.BitSharesConfig, **kwargs)
        except:
            raise APIUnavailable("BitShares API seems to be down!")

    def executeOp(self, op, wif):
        ops = [transactions.Operation(op)]
        ops = transactions.addRequiredFees(self.rpc.ws, ops, "1.3.0")
        expiration = transactions.formatTimeFromNow(30)
        ref_block_num, ref_block_prefix = transactions.getBlockParams(self.rpc.ws)
        tx = transactions.Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops
        )
        tx = tx.sign([wif], self.rpc.prefix)
        tx = transactions.JsonObj(tx)

        self.connect()
        if not self.nobroadcast:
            try:
                self.rpc.ws.broadcast_transaction(tx, api="network_broadcast")
            except:
                import traceback
                print(traceback.format_exc())
                raise BroadcastingError("Broadcasting error")
        else:
            print("Not broadcasting anything!")

        pprint(tx)

        return tx

    def check_account_exists(self, name):
        self.connect()
        try:
            account = self.rpc.ws.get_account(name, num_retries=0)
            if account:
                return True
            else:
                return False
        except:
            account = self.rpc.ws.get_account(name, num_retries=0)
            return False

    def create_account(self, data):
        name = data.get("name", None)

        owner_key = data.get("owner_key", None)
        active_key = data.get("active_key", None)
        memo_key = data.get("memo_key", None)

        if not owner_key or not active_key or not memo_key:
            raise MissingPublicKeys("Not all required public keys have been provided")

        # Get registrar
        registrar = data.get("registrar", config.registrar)

        # Get referrer
        referrer = data.get("referrer", None)
        if not referrer:
            referrer = config.default_referrer

        # Get referrer percentage
        referrer_percent = data.get("referrer_percent", config.referrer_percent)

        # Get wif
        wif = getattr(config, "wif", None)
        if not wif:
            raise MissingKeyError("We don't have a private key!")

        # Try connect to witness node
        self.connect()
        registrar = self.rpc.ws.get_account(registrar)
        referrer = self.rpc.ws.get_account(referrer)

        if not referrer:
            raise Exception("Unknown referrer!")
        if not registrar:
            raise Exception("Unknown registrar!")

        s = {"fee": {"amount": 100,
                     "asset_id": "1.3.0"
                     },
             "registrar": registrar["id"],
             "referrer": referrer["id"],
             "referrer_percent": int(referrer_percent),
             "name": name,
             "owner": {"weight_threshold": 1,
                       "account_auths": [],
                       'key_auths': [[owner_key, 1]],
                       "address_auths": []
                       },
             "active": {"weight_threshold": 1,
                        "account_auths": [],
                        'key_auths': [[active_key, 1]],
                        "address_auths": []
                        },
             "options": {"memo_key": memo_key,
                         "voting_account": "1.2.5",
                         "num_witness": 0,
                         "num_committee": 0,
                         "votes": [],
                         "extensions": []
                         },
             "extensions": {},
             "prefix" : self.rpc.prefix
             }
        pprint(s)
        op = transactions.Account_create(**s)

        self.connect()
        self.executeOp(op, wif)
