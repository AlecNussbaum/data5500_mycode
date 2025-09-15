#!/bin/bash

# Check if VS Code Server is already running
if ps -ef | grep -v grep | grep code-server > /dev/null
then
    echo "VS Code Server is already running."
else
    echo "Starting VS Code Server on port 443..."
    sudo code-server --config /home/ubuntu/.config/code-server/config.yaml --bind-addr 0.0.0.0:443 --cert /home/ubuntu/.config/code-server/selfsigned.crt --cert-key /home/ubuntu/.config/code-server/selfsigned.key /home/ubuntu > ~/code-server.log 2>&1 &
    echo "VS Code Server started on port 443."
fi
