#!/bin/sh

doc_str="Usage: ./run.sh
    example: ./run.sh app/venom_auto.py
"

mkdir -p log
mkdir -p tmp
# if have argument, use it as file name
if [ $# -gt 0 ]; then
    pf=$1
else
    pf="app/x.py"
fi


file_name=${pf##*/}
today=$(date '+%Y-%m-%d_%H:%M:%S')
file_name_log="log/${file_name%.*}_${today}.log"

# set pipenv path
if [[ -f "$HOME/.pyenv/shims/pipenv" ]]; then
  pipenv="$HOME/.pyenv/shims/pipenv"
elif [[ -f "$HOME/.local/bin/pipenv" ]]; then
  pipenv="$HOME/.local/bin/pipenv"
elif [[ -f "/opt/homebrew/bin/pipenv" ]]; then
  pipenv="/opt/homebrew/bin/pipenv"
elif [[ -f "/usr/local/bin/pipenv" ]]; then
  pipenv="/usr/local/bin/pipenv"
else
  echo "pipenv application not found"
fi
ptp=`pwd`
echo "Running PYTHONPATH=$ptp $pipenv run python $pf"
PYTHONPATH=`pwd` $pipenv run python $pf 2>&1 | tee $file_name_log
echo "check file $file_name_log"