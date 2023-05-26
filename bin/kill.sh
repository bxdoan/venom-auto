#!/usr/bin/env bash
s=$BASH_SOURCE ; s=$(dirname "$s") ; s=$(cd "$s" && pwd) ; SCRIPT_HOME="$s"  # get SCRIPT_HOME=executed script's path, containing folder, cd & pwd to get container path
HOME_REPO="$SCRIPT_HOME/.."
HOME_SCRIPT="$HOME_REPO/app/scripts"

STARTTIME=$(date +%s)
function print_exe_time() {
    STARTTIME=${1}
    ENDTIME=$(date +%s)
    EXE_TIME=$((${ENDTIME} - ${STARTTIME}))
    printf "
It takes ${GR}%s${EC} seconds to complete this script...\n" " ${EXE_TIME}"
}

key_word=$1
ps aux | grep "$key_word" | awk '{print $2}' | xargs kill -9 $1

print_exe_time "${STARTTIME}"
