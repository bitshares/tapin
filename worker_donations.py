import yaml
from pprint import pprint
import sys
import json
from bitshares import BitShares
from bitshares.account import Account
from bitshares.blockchain import Blockchain
import logging
log = logging.getLogger(__name__)

config = yaml.load(open("config.yml").read())

bitshares = BitShares(
    "wss://node.testnet.bitshares.eu",
    keys=[config["wif"]],
    nobroadcast=False
)


def run(begin=None, end=None):

    blockchain = Blockchain(
        mode="head",
        bitshares_instance=bitshares
    )

    for op in blockchain.stream(
        opNames=["account_create"]
    ):
        blockid = op.get("block_num")
        timestamp = op.get("timestamp")

        if not blockid % 100:
            print("Blockid: %d (%s)" % (blockid, timestamp), flush=True)

        try:
            pprint(bitshares.transfer(
                op["op"][1]["name"],
                config["donation_amount"], config["donation_asset"],
                account=config["registrar"]
            ))
        except Exception as e:
            log.error(str(e))
            pass


if __name__ == '__main__':
    run()
