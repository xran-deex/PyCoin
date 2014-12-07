#/bin/bash

export PYTHONPATH=:./lib

python lib/GUI/gui.py > /dev/null 2>&1

# if the above failed, try starting with python3...
if [ $? != 0 ]
then
  python3 lib/GUI/gui.py
fi
