import os
import time

from tome.command import tome_command
from tome.api.output import TomeOutput


@tome_command()
def monitor(tome_api, parser, *args):
    """Monitor system usage including CPU, memory, and disk."""
    parser.add_argument("--cpu", action="store_true", help="Monitor CPU usage in real-time")
    parser.add_argument("--memory", action="store_true", help="Monitor memory usage in real-time")
    parser.add_argument("--disk", action="store_true", help="Display disk usage")
    args = parser.parse_args(*args)

    import psutil

    tome_output = TomeOutput()

    if not any([args.cpu, args.memory, args.disk]):
        # Default to all if no specific option is provided
        args.cpu = args.memory = args.disk = True

    if args.disk:
        disk_usage = psutil.disk_usage("/")
        tome_output.info(f"Disk Usage: {disk_usage.percent}% used")
        tome_output.info(f"Total: {disk_usage.total / (1024**3):.2f} GB")
        tome_output.info(f"Used: {disk_usage.used / (1024**3):.2f} GB")
        tome_output.info(f"Free: {disk_usage.free / (1024**3):.2f} GB")

    if args.cpu:
        cpu_usage = psutil.cpu_percent(interval=1)
        tome_output.info(f"CPU Usage: {cpu_usage}%")

    if args.memory:
        memory_info = psutil.virtual_memory()
        tome_output.info(f"Memory Usage: {memory_info.percent}%")
        tome_output.info(f"Total: {memory_info.total / (1024**3):.2f} GB")
        tome_output.info(f"Used: {memory_info.used / (1024**3):.2f} GB")
        tome_output.info(f"Available: {memory_info.available / (1024**3):.2f} GB")
        tome_output.info(f"Free: {memory_info.free / (1024**3):.2f} GB")
