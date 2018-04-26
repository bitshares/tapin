import requests
from pprint import pprint

data =  {
    "account":{
        "name":"faucet-test-21",
        "owner_key":"BTS5WaszCsqVN9hDkXZPMyiUib3dyrEA4yd5kSMgu28Wz47B3wUqa",
        "active_key":"BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
        "memo_key":"BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
        "real_name": "Foobar Hans",
        "email": "asfasfas@asfas.com"
    }
}

ret = requests.post("http://localhost:5000/api/v1/accounts", json=data)
assert ret.status_code == 200, ret.text

pprint(ret.json())
