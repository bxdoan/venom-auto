#!/bin/sh

# pull latest code
git pull

# set pipenv path
if [ `uname` = "Darwin" ]; then
    pipenv="/Users/`whoami`/.local/bin/pipenv"
else
    pipenv="/home/`whoami`/.pyenv/shims/pipenv"
fi

rm -rf .venv
$pipenv sync
$pipenv run pip install git+https://github.com/bxdoan/dongle-lte-api.git
