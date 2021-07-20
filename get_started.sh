#!/bin/bash

mkvirtualenv -p $(which python3.8) $(basename "$PWD") && workon $(basename "$PWD")

pip install -r requirements.txt
