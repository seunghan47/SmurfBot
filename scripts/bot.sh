#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
BOT_DIR="$DIR/../src"
LOG_DIR="$DIR/../logs"

function start(){
	if  pgrep -fv "start.py" > /dev/null; then
		nohup python3 "$BOT_DIR/start.py" >> "$LOG_DIR/logs.out" &
		ps -eo pid,command | awk ' /"$BOT_DIR/start.py"/ { print $1 }' > "$DIR/bot_pid"
		echo "bot has been started"
	fi
}

function stop(){
	if  pgrep -f "start.py" > /dev/null; then
		echo "bot is up. killing bot"
		kill -15 "$(cat "$DIR/bot_pid")"
	else
		echo "bot isn't up. nothing to kill"
	fi
}

case $1 in
	start)
		mkdir -p "$LOG_DIR"
		start
		;;
	stop)
		stop
		;;
	restart)
		stop
		start
		;;
	*)
		echo "invalid option. Options are start, stop, or restart"
esac
