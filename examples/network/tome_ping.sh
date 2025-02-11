#!/bin/bash
# tome_description: Script to ping an IP address or URL. Arguments: <IP or URL>.

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <IP or URL>"
    exit 1
fi

ping -c 4 "$1"
