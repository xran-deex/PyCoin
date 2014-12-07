#/bin/bash

export PYTHONPATH=:.

python GUI/gui.py > /dev/null 2>&1

# if the above failed, try starting with python3...
if [ $? != 0 ]
then
  python3 GUI/gui.py
fi