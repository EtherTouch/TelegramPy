#!/bin/bash

file_dir=$( realpath "$0" | sed 's|\(.*\)/.*|\1|' )
cd $file_dir

export PYTHONPATH="${PYTHONPATH}:${file_dir}"
echo $PYTHONPATH


# run it in a while loop so that it run indefinitely even after crash due to network isssue
while true; do
    ./env/bin/python3 ./main.py
    echo "App crashed. Restarting in 60 seconds"
    sleep 60  # 60 seconds = 1 minutes
done

sleep 60
