#! /usr/bin/env bash

### BEGIN INIT INFO
# Provides:          fancontrol.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
### END INIT INFO

# Carry out specific functions when asked to by the system

case "$1" in
    start)
        echo "Starting Discord Bot"
        source /home/pi/discord_bot_collection/.venv/bin/activate &
        /home/pi/discord_bot_collection/.venv/bin/python /home/pi/discord_bot_collection/bot.py &
        ;;
    stop)
        echo "Stopping Discord Bot"
        pkill -f /home/pi/discord_bot_collection/bot.py
        ;;
    *)
        echo "Usage: ./bot.sh {start|stop}"
        exit 1
        ;;
esac

exit 0
