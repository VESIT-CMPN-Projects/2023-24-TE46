#!/bin/bash
sudo apt install python3 python3-pip libsane-dev xsane libsane-dev python-tk
python -m venv ./venv
source ./venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
