#!/usr/bin/env bash

export FLASK_APP=index.py
export FLASK_DEBUG=1
python -m flask run --host=localhost
