#!/bin/bash

# This script is intended for Raspberry Pi OS only. It monitors TelegramPy
# And reboots the Raspberry Pi if TelegramPy stops running.

file_dir=$( realpath "$0" | sed 's|\(.*\)/.*|\1|' )
cd $file_dir

export PYTHONPATH="${PYTHONPATH}:${file_dir}"
echo $PYTHONPATH


./env/bin/python3 ./telegrampy/extras/monitor_telegrampy.py

