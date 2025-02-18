#!/bin/sh
echo "1 0 * * * /usr/local/bin/python /app/fetching_script.py" | crontab -
service cron start