#!/bin/sh

# set pipenv path
if [ `uname` = "Darwin" ]; then
    pipenv="/Users/`whoami`/.local/bin/pipenv"
else
    pipenv="/home/`whoami`/.pyenv/shims/pipenv"
fi

rm -rf .venv
$pipenv sync
$pipenv run pip install git+https://github.com/bxdoan/dongle-lte-api.git
$pipenv run pip install -e 'git+https://github.com/jdholtz/undetected-chromedriver.git@29551bd27954dacaf09864cf77935524db642c1b#egg=undetected_chromedriver'
