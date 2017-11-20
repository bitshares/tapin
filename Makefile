all:
	cython -2 --embed manage.py -o faucet.c
	gcc -g -O2 -o faucet faucet.c `python-config --includes --ldflags`
