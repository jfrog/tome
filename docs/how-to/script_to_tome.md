# How to migrate a script to tome

If you want to add your current scripts to tome you need to: 

- Add the `tome_` prefix name only to the scripts that you want to use as tome command.
- Add a single comment at top of the script with the `tome_description:`.
- Store it as an others tome scripts in a folder to have a tome namespace.

Imagine that you have following `ping.sh` bash script and you want to use it as `tome network:ping`.

```bash
#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <IP or URL>"
    exit 1
fi

ping -c 4 "$1"
```

```bash
% /bin/bash ping.sh 8.8.8.8
PING 8.8.8.8 (8.8.8.8): 56 data bytes
64 bytes from 8.8.8.8: icmp_seq=0 ttl=117 time=5.569 ms
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=9.094 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=4.945 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=117 time=5.347 ms

--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 4.945/6.239/9.094/1.664 ms
```

First of all, copy this file to an empty folder, add the `tome_` prefix and a `tome_description`.

```bash
% tree
└── my_script
    └── network
        └── tome_ping.sh
```

```bash
#!/bin/bash
# tome_description: Script to ping an IP address or URL. Arguments: <IP or URL>.

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <IP or URL>"
    exit 1
fi

ping -c 4 "$1"
```

Install your command as editable.

```bash
% tome install my_script -e
```

Now, you can use your command like an other tome commands and edit it as usual.

```bash
 % tome list
Results for '*' pattern:

🌐 network commands
 network:ping (e)        Script to ping an IP address or URL. Arguments: <IP or URL>.
```

```bash
% tome network:ping 8.8.8.8
PING 8.8.8.8 (8.8.8.8): 56 data bytes
64 bytes from 8.8.8.8: icmp_seq=0 ttl=117 time=3.526 ms
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=3.878 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=4.606 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=117 time=6.007 ms

--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 3.526/4.504/6.007/0.951 ms
```
