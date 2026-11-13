#!/usr/bin/env python3
"""Part 1: Basic System Information (Linux /proc based)."""
import os
import platform
import time
from datetime import datetime


def get_meminfo():
    info = {}
    with open('/proc/meminfo', 'r', encoding='utf-8') as f:
        for line in f:
            key, rest = line.split(':', 1)
            # values in kB
            parts = rest.strip().split()
            info[key] = int(parts[0]) if parts else 0
    return info


def main():
    mem = get_meminfo()
    total_kb = mem.get('MemTotal', 0)
    avail_kb = mem.get('MemAvailable', mem.get('MemFree', 0))

    total_gb = total_kb / (1024 * 1024)
    avail_gb = avail_kb / (1024 * 1024)

    print("=" * 60)
    print("PART 1: BASIC SYSTEM INFORMATION")
    print("=" * 60)
    print(f"Operating System      : {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Distribution/Kernel   : {platform.platform()}")
    print(f"Number of CPU cores   : {os.cpu_count()}")
    print(f"Total RAM             : {total_gb:.2f} GB ({total_kb} kB)")
    print(f"Available RAM         : {avail_gb:.2f} GB ({avail_kb} kB)")
    print(f"Current system time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
