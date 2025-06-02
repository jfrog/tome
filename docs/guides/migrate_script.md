# How to Migrate and Create Shell Scripts with Tome

If you have existing shell scripts or want to create new ones, you can easily
integrate them into **tome**. **tome** can discover and run common shell script
types (such as `.sh`, `.bash`, `.bat`, and `.ps1`) if they follow a few simple
conventions:

* **Filename Prefix:** Scripts intended to be discovered by **tome** should have
  their filenames prefixed with `tome_` (e.g., `tome_mybackup.sh`).
* **Description Comment:** Include a special comment line at or near the top of
  your script: `# tome_description: Your command description here` (use `REM
  tome_description:` for `.bat` files).
* **Directory Structure for Namespace:** Place your script inside a
  subdirectory. The name of this subdirectory will become the **Namespace** for
  your command within its **Tome**.

Let's walk through an example, starting by generating a shell script template
with `tome new` and then customizing it.

## Example: Creating a `network:ping` Shell Script with `tome new`

We'll create a `ping` command in the `network` namespace that will be a shell
script.

### Step 1: Generate and Prepare the Script

1.  First, create a directory that will serve as the **Origin** for this
    **Tome** (e.g., `my-network-scripts`) and navigate into it.

        $ mkdir my-network-scripts
        $ cd my-network-scripts

2.  Use `tome new` with the `--type=sh` flag to generate a shell script template
    for `network:ping`:

        $ tome new network:ping --type=sh --description "Pings an IP address or URL. Arguments: <IP or URL>"
        Generated script: network/tome_ping.sh

    Your structure should now look like this:

        my-network-scripts/
        └── network/
            └── tome_ping.sh # This is the generated template

### Step 2: Customize the Generated Script

The generated `network/tome_ping.sh` will contain a basic template. Open it and
replace its content with the specific logic for our ping command:

    #!/bin/bash
    # tome_description: Pings an IP address or URL. Arguments: <IP or URL>

    if [ "$#" -ne 1 ]; then
        echo "Usage: $0 <IP or URL>"
        exit 1
    fi

    ping -c 4 "$1"

The description you provided to `tome new` (or edited in the file) will be shown
by `tome list`. The script itself takes one argument (`$1`), which will be the
IP or URL to ping.

### Step 3: Install the Tome

Navigate to your `my-network-scripts` directory (if you're not already there).
Then, install it as an editable **Tome**:

    $ tome install . -e
    Configured editable installation ...
    Installed source: ...

### Step 4: Use Your New Shell Command

Now your shell script is a **tome** **Command**!

List available commands (you might see others if you have more **Tomes**
installed):

    $ tome list

Output should include:

      🌐 network commands
         network:ping-sh (e)  Pings an IP address or URL. Arguments: <IP or URL>

**Note on Shell Command Naming:** You might notice the command is listed as
`network:ping-sh`. When **tome** discovers shell scripts (files not ending in
`.py` but recognized as executable scripts like `.sh`, `.bat`, etc.), it often
appends a suffix based on the script's extension (e.g., `-sh`, `-bat`) to the
command name. This helps differentiate if you had, for example, both a Python
and a shell version of a `ping` command in the same namespace. So, you'd run it
as `tome network:ping-sh`.

Run your command:

    $ tome network:ping-sh 8.8.8.8
    PING 8.8.8.8 (8.8.8.8): 56 data bytes
    64 bytes from 8.8.8.8: icmp_seq=0 ttl=119 time=9.543 ms
    64 bytes from 8.8.8.8: icmp_seq=1 ttl=119 time=11.825 ms
    64 bytes from 8.8.8.8: icmp_seq=2 ttl=119 time=43.971 ms
    64 bytes from 8.8.8.8: icmp_seq=3 ttl=119 time=27.419 ms

    --- 8.8.8.8 ping statistics ---
    4 packets transmitted, 4 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 9.543/23.189/43.971/13.831 ms

Arguments passed after `tome network:ping-sh` are forwarded directly to your
`tome_ping.sh` script. Since it's an editable install, you can continue to
modify `tome_ping.sh`, and the changes will be live immediately when you run it
via **tome**.

That's it! You've successfully created (by generating and then customizing) a
shell script to be managed by **tome**. If you have an *existing* script, you
would simply place it in the correct namespace folder, ensure it has the
`tome_description` comment (and the `tome_` filename prefix if `tome new` didn't
create it), and then install its parent **Tome**. This process applies to other
shell script types like `.bat` or `.ps1` as well (using `REM tome_description:`
for `.bat` files).
