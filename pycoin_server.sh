#/bin/bash

export PYTHONPATH=:./lib

#echo 'PyCoin server starting...'

python3 lib/P2P/p2pserver.py

# if the above failed, try starting with python...
if [ $? != 0 ]
then
  python lib/P2P/p2pserver.py
fi
