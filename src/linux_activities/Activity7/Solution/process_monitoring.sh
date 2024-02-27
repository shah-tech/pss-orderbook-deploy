#!/bin/bash

# This script demonstrates how to produce meaningful logs for process monitoring in Linux

# Set the log file location
log_file="/home/ec2-user/linux_activities/Monitoring/process_monitor.log"

# Set the process name to monitor
process_name=$1

# Check if the process is running
if pgrep "$process_name" > /dev/null
then
  # If the process is running, log a message to the log file
  echo "$(date): $process_name is running" >> "$log_file"
else
  # If the process is not running, log a message to the log file
  echo "$(date): $process_name is not running" >> "$log_file"
fi

# Check the exit code of the previous command
if [ $? -eq 0 ]
then
  # If the exit code is 0, the process is running
  # Log a message to the log file
  echo "$(date): $process_name check completed successfully" >> "$log_file"
else
  # If the exit code is not 0, the process is not running
  # Log a message to the log file
  echo "$(date): $process_name check failed" >> "$log_file"
fi
