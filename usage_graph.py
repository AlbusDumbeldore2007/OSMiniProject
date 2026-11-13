#!/usr/bin/env python3
"""Part 3: Record CPU & Memory usage every 1s for 15s and visualize results.

Generates: outputs/cpu_memory_usage.csv, outputs/cpu_graph.png, outputs/memory_graph.png
Tries matplotlib if available; otherwise creates simple SVG charts and converts to PNG via ImageMagick.
"""
import csv
import os
import subprocess
import time


def read_cpu_times():
    with open('/proc/stat', 'r', encoding='utf-8') as f:
        parts = f.readline().split()
    vals = list(map(int, parts[1:]))
    idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
    total = sum(vals)
    return total, idle


def read_mem_usage_pct():
    info = {}
    with open('/proc/meminfo', 'r', encoding='utf-8') as f:
        for line in f:
            key, rest = line.split(':', 1)
            info[key] = int(rest.strip().split()[0])
    total = info.get('MemTotal', 1)
    avail = info.get('MemAvailable', info.get('MemFree', 0))
    used_pct = 100.0 * (total - avail) / total
    return used_pct


def make_svg_line_chart(values, title, ylabel, out_svg, color='#2563eb', width=800, height=400):
    if not values:
        return
    pad_l, pad_r, pad_t, pad_b = 70, 30, 50, 60
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    y_min = 0.0
    y_max = max(100.0, max(values) * 1.1)
    n = len(values)

    def x(i):
        if n == 1:
            return pad_l + plot_w / 2
        return pad_l + (i / (n - 1)) * plot_w

    def y(v):
        return pad_t + plot_h - ((v - y_min) / (y_max - y_min)) * plot_h

    points = ' '.join(f"{x(i):.2f},{y(v):.2f}" for i, v in enumerate(values))
    # grid and labels
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    lines.append('<rect width="100%" height="100%" fill="white"/>')
    lines.append(f'<text x="{width/2}" y="28" text-anchor="middle" font-size="20" font-family="sans-serif" font-weight="bold">{title}</text>')
    lines.append(f'<text x="{pad_l + plot_w/2}" y="{height-15}" text-anchor="middle" font-size="14" font-family="sans-serif">Time (seconds)</text>')
    lines.append(f'<text x="20" y="{pad_t + plot_h/2}" text-anchor="middle" font-size="14" font-family="sans-serif" transform="rotate(-90 20 {pad_t + plot_h/2})">{ylabel}</text>')
    # axes
    lines.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+plot_h}" stroke="#333" stroke-width="1"/>')
    lines.append(f'<line x1="{pad_l}" y1="{pad_t+plot_h}" x2="{pad_l+plot_w}" y2="{pad_t+plot_h}" stroke="#333" stroke-width="1"/>')
    # y ticks
    for t in range(0, 101, 20):
        if t > y_max:
            continue
        yy = y(t)
        lines.append(f'<line x1="{pad_l-5}" y1="{yy:.2f}" x2="{pad_l+plot_w}" y2="{yy:.2f}" stroke="#ddd" stroke-width="1"/>')
        lines.append(f'<text x="{pad_l-10}" y="{yy+4:.2f}" text-anchor="end" font-size="12" font-family="sans-serif">{t}</text>')
    # x ticks
    for i in range(n):
        xx = x(i)
        lines.append(f'<line x1="{xx:.2f}" y1="{pad_t+plot_h}" x2="{xx:.2f}" y2="{pad_t+plot_h+5}" stroke="#333"/>')
        lines.append(f'<text x="{xx:.2f}" y="{pad_t+plot_h+20}" text-anchor="middle" font-size="12" font-family="sans-serif">{i+1}</text>')
    # line and points
    lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{points}"/>')
    for i, v in enumerate(values):
        lines.append(f'<circle cx="{x(i):.2f}" cy="{y(v):.2f}" r="4" fill="{color}"/>')
    lines.append('</svg>')
    with open(out_svg, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def save_graph(values, title, ylabel, png_path, color):
    svg_path = png_path.rsplit('.', 1)[0] + '.svg'
    make_svg_line_chart(values, title, ylabel, svg_path, color=color)
    # try matplotlib first
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        xs = list(range(1, len(values) + 1))
        plt.figure(figsize=(8, 4))
        plt.plot(xs, values, marker='o', color=color)
        plt.title(title)
        plt.xlabel('Time (seconds)')
        plt.ylabel(ylabel)
        plt.ylim(0, max(100, max(values) * 1.1))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(png_path, dpi=120)
        plt.close()
        return 'matplotlib'
    except Exception:
        pass
    # fallback: convert SVG to PNG
    try:
        subprocess.run(['convert', svg_path, png_path], check=True, capture_output=True)
        return 'svg-convert'
    except Exception:
        # keep SVG as fallback
        return 'svg-only'


def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(out_dir, exist_ok=True)

    intervals = 15
    cpu_values = []
    mem_values = []

    prev_total, prev_idle = read_cpu_times()
    print("Recording CPU and memory usage every 1 second for 15 seconds...")
    for i in range(intervals):
        time.sleep(1.0)
        cur_total, cur_idle = read_cpu_times()
        total_d = cur_total - prev_total
        idle_d = cur_idle - prev_idle
        cpu_pct = 100.0 * (total_d - idle_d) / total_d if total_d else 0.0
        mem_pct = read_mem_usage_pct()
        cpu_values.append(round(cpu_pct, 2))
        mem_values.append(round(mem_pct, 2))
        prev_total, prev_idle = cur_total, cur_idle
        print(f"  Second {i+1:2d}: CPU={cpu_pct:5.2f}%  Memory={mem_pct:5.2f}%")

    csv_path = os.path.join(out_dir, 'cpu_memory_usage.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['second', 'cpu_percent', 'memory_percent'])
        for i, (c, m) in enumerate(zip(cpu_values, mem_values), start=1):
            w.writerow([i, c, m])

    cpu_png = os.path.join(out_dir, 'cpu_graph.png')
    mem_png = os.path.join(out_dir, 'memory_graph.png')
    m1 = save_graph(cpu_values, 'CPU Usage vs Time (15s)', 'CPU Usage (%)', cpu_png, '#2563eb')
    m2 = save_graph(mem_values, 'Memory Usage vs Time (15s)', 'Memory Usage (%)', mem_png, '#16a34a')

    print("\nSaved outputs:")
    print(f"  {csv_path}")
    print(f"  {cpu_png} ({m1})")
    print(f"  {mem_png} ({m2})")


if __name__ == '__main__':
    main()
