#!/bin/bash

# export WORKON_HOME=~/Envs
source $(which virtualenvwrapper.sh)
# export WORKON_HOME=~/Envs

VENV_NAME=$(basename "$PWD")
echo $VENV_NAME

mkvirtualenv -p $(which python3.8) $VENV_NAME

# workon $VENV_NAME

if ! command -v poetry &>/dev/null; then
    echo "poetry could not be found. See: https://python-poetry.org/docs/ for installation"
    exit
else
    poetry install
fi
