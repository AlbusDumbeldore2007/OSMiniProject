#!/usr/bin/env python3
"""Part 2: Process List Viewer - top 5 processes by CPU usage (Linux /proc)."""
import os
import time


def read_total_cpu():
    with open('/proc/stat', 'r', encoding='utf-8') as f:
        parts = f.readline().split()
    # user nice system idle iowait irq softirq steal guest guest_nice
    vals = list(map(int, parts[1:]))
    idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
    total = sum(vals)
    return total, idle


def read_proc_cpu(pid):
    try:
        with open(f'/proc/{pid}/stat', 'r', encoding='utf-8') as f:
            data = f.read()
        # name can contain spaces and is in parens
        rparen = data.rfind(')')
        after = data[rparen + 2 :].split()
        # fields after comm start at state (index 0 here) -> utime=11, stime=12 in after? stat: pid (comm) state ppid ...
        # after split starting at state: [state, ppid, pgrp, session, tty_nr, tpgid, flags, minflt, cminflt, majflt, cmajflt, utime, stime,...]
        utime = int(after[11])
        stime = int(after[12])
        with open(f'/proc/{pid}/comm', 'r', encoding='utf-8', errors='replace') as f:
            name = f.read().strip()
        return utime + stime, name
    except Exception:
        return None


def read_mem_total_kb():
    with open('/proc/meminfo', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('MemTotal:'):
                return int(line.split()[1])
    return 1


def read_proc_mem_kb(pid):
    try:
        with open(f'/proc/{pid}/status', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('VmRSS:'):
                    return int(line.split()[1])
        return 0
    except Exception:
        return 0


def sample_processes():
    procs = {}
    for entry in os.listdir('/proc'):
        if not entry.isdigit():
            continue
        pid = int(entry)
        res = read_proc_cpu(pid)
        if res is None:
            continue
        ticks, name = res
        mem_kb = read_proc_mem_kb(pid)
        procs[pid] = {'ticks': ticks, 'name': name, 'mem_kb': mem_kb}
    return procs


def main():
    mem_total = read_mem_total_kb()
    t1_total, t1_idle = read_total_cpu()
    p1 = sample_processes()
    time.sleep(1.0)
    t2_total, t2_idle = read_total_cpu()
    p2 = sample_processes()

    total_delta = max(t2_total - t1_total, 1)
    rows = []
    for pid, cur in p2.items():
        prev = p1.get(pid)
        if not prev:
            continue
        proc_delta = cur['ticks'] - prev['ticks']
        cpu_pct = 100.0 * proc_delta / total_delta
        mem_pct = 100.0 * cur['mem_kb'] / mem_total if mem_total else 0.0
        rows.append((pid, cur['name'], cpu_pct, mem_pct))

    rows.sort(key=lambda r: r[2], reverse=True)
    top5 = rows[:5]

    print("=" * 78)
    print("PART 2: TOP 5 RUNNING PROCESSES (by CPU usage over 1s sample)")
    print("=" * 78)
    print(f"{'PID':>8}  {'Process Name':<35}  {'CPU %':>10}  {'Memory %':>10}")
    print("-" * 78)
    for pid, name, cpu, mem in top5:
        disp = (name[:32] + '...') if len(name) > 35 else name
        print(f"{pid:>8}  {disp:<35}  {cpu:>9.2f}%  {mem:>9.2f}%")
    print("=" * 78)


if __name__ == '__main__':
    main()
