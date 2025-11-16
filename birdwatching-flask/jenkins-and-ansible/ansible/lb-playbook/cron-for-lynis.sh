#!/bin/bash

sudo crontab -e

cron='*/30 * * * * sudo lynis audit system >> /vagrant/storage/lynis-audit-database-result-$(date +\%d-\%m-\%Y-\%H-\%M-\%S).txt'
# │ │ │ │ │
# │ │ │ │ │
# │ │ │ │ └───── day of week (0 - 6) (0 to 6 are Sunday to Saturday, or use names; 7 is Sunday, the same as 0)
# │ │ │ └────────── month (1 - 12)
# │ │ └─────────────── day of month (1 - 31)
# │ └──────────────────── hour (0 - 23)
# └───────────────────────── min (0 - 59)

# Escape all the asterisks so we can grep for it
cron_escaped=$(echo "$cron" | sed s/\*/\\\\*/g)

# Check if cron job already in crontab
crontab -l | grep "${cron_escaped}"
if [[ $? -eq 0 ]]; then
  echo "Crontab already exists. Exiting..."
  exit
else
  # Write out current crontab into temp file
  crontab -l >mycron
  # Append new cron into cron file
  echo "$cron" >>mycron
  # Install new cron file
  crontab mycron
  # Remove temp file
  rm mycron
fi

