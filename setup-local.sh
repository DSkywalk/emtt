#!/bin/bash

set -e

virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cp -v config_example.json config.json
