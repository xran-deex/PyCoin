#/bin/bash

export PYTHONPATH=:.

echo 'PyCoin server starting...'

python3 P2P/p2pserver.py

# if the above failed, try starting with python...
if [ $? != 0 ]
then
  python P2P/p2pserver.py
fi