import click
import requests
from pprint import pprint

from bitsharesbase.account import PrivateKey

p = PrivateKey("5J539ijxkg4tw7zP95spwek5YqoD39zWp2kKMA6PBqpmukHL6yP")

data =  {
    "account": {
        "name": "test-faucet-21",
        "owner_key": str(p.pubkey),
        "active_key": str(p.pubkey),
        "memo_key": str(p.pubkey),
        "real_name":  "Foobar Hans",
        "email":  "asfasfas@asfas.com"
    }
}


@click.command()
@click.option("--endpoint", default="http://localhost:5000")
@click.argument("name", default="test-faucet-21")
def main(endpoint, name):

    data["account"]["name"] = name

    pprint(data)

    ret = requests.post(
        endpoint + "/api/v1/accounts",
        json=data)

    assert ret.status_code == 200, ret.text

    pprint(ret.json())


if __name__ == "__main__":
    main()
