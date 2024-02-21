#!/bin/bash

PROJ=/home/jon/proj/efj/toolkit/

cd $PROJ
python3 -m venv venv-shiv
source venv-shiv/bin/activate
pip install shiv
pip install wheel
shiv -c efjgui -o efjgui.pyw -p "/usr/bin/env python3" $PROJ
shiv -c efj -o efj.py -p "/usr/bin/env python3" $PROJ
deactivate
rm -r venv-shiv
