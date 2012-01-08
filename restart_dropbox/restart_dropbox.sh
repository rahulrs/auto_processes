#!/bin/sh

# Kill and restart dropbox every 5th minute of the hour
# Run this script on ray

killall dropbox
~/.dropbox-dist/dropboxd &
