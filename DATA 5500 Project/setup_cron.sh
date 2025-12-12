#!/bin/bash
# setup_cron.sh - Set up crontab for stock trading algorithm

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH=$(which python3)
SCRIPT_PATH="$SCRIPT_DIR/stock_trading.py"
LOG_PATH="$SCRIPT_DIR/trading.log"

# Create the cron job entry
# 9:00 AM ET = 14:00 UTC (standard time) or 13:00 UTC (daylight saving)
# Using 14:00 UTC for Eastern Standard Time
CRON_JOB="0 14 * * 1-5 cd $SCRIPT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $LOG_PATH 2>&1"

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -F "$SCRIPT_PATH") && {
    echo "Cron job already exists for this script."
    exit 0
}

# Add the cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Cron job added successfully!"
echo "Schedule: Monday-Friday at 9:00 AM ET (14:00 UTC)"
echo "Command: $CRON_JOB"
echo ""
echo "To verify, run: crontab -l"
echo "To view logs, run: tail -f $LOG_PATH"