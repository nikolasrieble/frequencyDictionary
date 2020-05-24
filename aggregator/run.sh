#!/usr/bin/env bash

# Write environment variables into file, so they can be made available to cron jobs
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env

cron
