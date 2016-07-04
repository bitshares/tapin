# Tapin

`tapin` is a python-based faucet for Graphene-based blockchains (e.g.  BitShares).

## Installation

* edit `config.py` and provide private keys and settings
* `python manage.py install`

## Usage

* `python manage.py runserver`

The faucet is then available at URL `http://localhost:5000`

## Deploy on Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Remark: Please understand the risks of exposing private keys to heroku!
