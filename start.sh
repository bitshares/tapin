#!/bin/bash

docker rmi bts-faucet
docker build -t bts-faucet .
docker run -p 9090:9090/tcp -it --rm --name bts-faucet bts-faucet
