#!/usr/bin/env bash
s=$BASH_SOURCE ; s=$(dirname "$s") ; s=$(cd "$s" && pwd) ; SCRIPT_HOME="$s"  # get SCRIPT_HOME=executed script's path, containing folder, cd & pwd to get container path
HOME_REPO="$SCRIPT_HOME/.."
HOME_SCRIPT="$HOME_REPO/app/scripts"

if [[ -f "$HOME/.pyenv/shims/pipenv" ]]; then
  pipenv="$HOME/.pyenv/shims/pipenv"
elif [[ -f "$HOME/.local/bin/pipenv" ]]; then
  pipenv="$HOME/.local/bin/pipenv"
elif [[ -f "/opt/homebrew/bin/pipenv" ]]; then
  pipenv="/opt/homebrew/bin/pipenv"
else
  echo "pipenv application not found"
fi

# if not found pipenv run python directly
if [[ -z "$pipenv" ]]; then
  echo "pipenv not found, run python directly"
  PYTHONPATH=`pwd` python3 "$HOME_SCRIPT/otp.py" "$@"
else
  PYTHONPATH=`pwd` $pipenv run python3 "$HOME_SCRIPT/otp.py" "$@"
fi

