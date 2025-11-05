#!/usr/bin/env python3
"""
LAN9662 Dual-Board vs Single-Board Comparison Analysis
Compares performance metrics between dual-board and single-board configurations
"""

import re
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def parse_sockperf_file(filename):
    """Parse sockperf output file and extract key metrics"""
    with open(filename, 'r') as f:
        content = f.read()

    results = {}

    # Extract avg-latency and std-dev
    latency_match = re.search(r'avg-latency=(\d+\.\d+)\s+\(std-dev=(\d+\.\d+)\)', content)
    if latency_match:
        results['avg_latency_us'] = float(latency_match.group(1))
        results['std_dev_us'] = float(latency_match.group(2))
        results['jitter_us'] = results['std_dev_us']

    # Extract percentiles
    percentiles = {}
    for match in re.finditer(r'percentile\s+([\d.]+)\s+=\s+([\d.]+)', content):
        pct = float(match.group(1))
        val = float(match.group(2))
        percentiles[pct] = val
    results['percentiles'] = percentiles

    # Extract min/max
    min_match = re.search(r'<MIN>\s+observation\s+=\s+([\d.]+)', content)
    max_match = re.search(r'<MAX>\s+observation\s+=\s+([\d.]+)', content)
    if min_match:
        results['min_latency_us'] = float(min_match.group(1))
    if max_match:
        results['max_latency_us'] = float(max_match.group(1))

    # Extract total observations
    obs_match = re.search(r'Total\s+(\d+)\s+observations', content)
    if obs_match:
        results['total_observations'] = int(obs_match.group(1))

    # Extract throughput info
    bw_match = re.search(r'BandWidth is ([\d.]+) MBps \(([\d.]+) Mbps\)', content)
    if bw_match:
        results['bandwidth_mbps'] = float(bw_match.group(2))
        results['bandwidth_MBps'] = float(bw_match.group(1))

    msg_rate_match = re.search(r'Message Rate is (\d+)', content)
    if msg_rate_match:
        results['msg_rate'] = int(msg_rate_match.group(1))

    return results

def main():
    # Parse dual-board results
    dual_tests = {
        'Ping-Pong (Default)': 'sockperf_pingpong_udp.txt',
        'Ping-Pong (64B)': 'sockperf_pingpong_64B.txt',
        'Ping-Pong (512B)': 'sockperf_pingpong_512B.txt',
        'Ping-Pong (1472B)': 'sockperf_pingpong_1472B.txt',
        'Under Load': 'sockperf_underload_udp.txt',
        'Throughput': 'sockperf_throughput_udp.txt',
    }

    # Parse single-board results
    single_tests = {
        'Ping-Pong (Default)': 'sockperf_single_pingpong_udp.txt',
        'Ping-Pong (64B)': 'sockperf_single_pingpong_64B.txt',
        'Ping-Pong (512B)': 'sockperf_single_pingpong_512B.txt',
        'Ping-Pong (1472B)': 'sockperf_single_pingpong_1472B.txt',
        'Under Load': 'sockperf_single_underload_udp.txt',
        'Throughput': 'sockperf_single_throughput_udp.txt',
    }

    dual_results = {}
    single_results = {}

    for test_name, filename in dual_tests.items():
        if Path(filename).exists():
            dual_results[test_name] = parse_sockperf_file(filename)
            print(f"✓ Parsed dual-board {test_name}")

    for test_name, filename in single_tests.items():
        if Path(filename).exists():
            single_results[test_name] = parse_sockperf_file(filename)
            print(f"✓ Parsed single-board {test_name}")

    # Create comprehensive comparison visualization
    fig = plt.figure(figsize=(18, 12))

    # Plot 1: Latency Comparison by Message Size
    ax1 = plt.subplot(3, 3, 1)
    msg_sizes = [14, 64, 512, 1472]
    ping_pong_tests = ['Ping-Pong (Default)', 'Ping-Pong (64B)', 'Ping-Pong (512B)', 'Ping-Pong (1472B)']

    dual_latencies = [dual_results[t]['avg_latency_us'] for t in ping_pong_tests if t in dual_results]
    single_latencies = [single_results[t]['avg_latency_us'] for t in ping_pong_tests if t in single_results]

    ax1.plot(msg_sizes[:len(dual_latencies)], dual_latencies, 'o-', linewidth=2, markersize=8,
             label='Dual Board', color='#e74c3c')
    ax1.plot(msg_sizes[:len(single_latencies)], single_latencies, 's-', linewidth=2, markersize=8,
             label='Single Board', color='#2ecc71')
    ax1.set_xlabel('Message Size (Bytes)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Latency (μs)', fontsize=11, fontweight='bold')
    ax1.set_title('Average Latency Comparison', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')

    # Plot 2: Jitter Comparison
    ax2 = plt.subplot(3, 3, 2)
    dual_jitters = [dual_results[t]['jitter_us'] for t in ping_pong_tests if t in dual_results]
    single_jitters = [single_results[t]['jitter_us'] for t in ping_pong_tests if t in single_results]

    ax2.plot(msg_sizes[:len(dual_jitters)], dual_jitters, 'o-', linewidth=2, markersize=8,
             label='Dual Board', color='#e74c3c')
    ax2.plot(msg_sizes[:len(single_jitters)], single_jitters, 's-', linewidth=2, markersize=8,
             label='Single Board', color='#2ecc71')
    ax2.set_xlabel('Message Size (Bytes)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Jitter (μs)', fontsize=11, fontweight='bold')
    ax2.set_title('Jitter Comparison', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')

    # Plot 3: Latency Improvement (%)
    ax3 = plt.subplot(3, 3, 3)
    improvements = []
    labels = []
    for i, test in enumerate(ping_pong_tests):
        if test in dual_results and test in single_results:
            dual_lat = dual_results[test]['avg_latency_us']
            single_lat = single_results[test]['avg_latency_us']
            improvement = ((dual_lat - single_lat) / dual_lat) * 100
            improvements.append(improvement)
            labels.append(f"{msg_sizes[i]}B")

    colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in improvements]
    bars = ax3.bar(labels, improvements, color=colors)
    ax3.set_ylabel('Improvement (%)', fontsize=11, fontweight='bold')
    ax3.set_title('Single-Board Latency Improvement', fontsize=12, fontweight='bold')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax3.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar, val in zip(bars, improvements):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%',
                ha='center', va='bottom' if val > 0 else 'top', fontweight='bold', fontsize=9)

    # Plot 4: Side-by-side latency comparison
    ax4 = plt.subplot(3, 3, 4)
    x_pos = np.arange(len(ping_pong_tests))
    width = 0.35

    ax4.bar(x_pos - width/2, dual_latencies, width, label='Dual Board', color='#e74c3c', alpha=0.8)
    ax4.bar(x_pos + width/2, single_latencies, width, label='Single Board', color='#2ecc71', alpha=0.8)

    ax4.set_ylabel('Latency (μs)', fontsize=11, fontweight='bold')
    ax4.set_title('Latency Side-by-Side Comparison', fontsize=12, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([t.replace('Ping-Pong ', '') for t in ping_pong_tests], rotation=15, ha='right')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')

    # Plot 5: Min/Max Latency Range Comparison
    ax5 = plt.subplot(3, 3, 5)
    for i, test in enumerate(ping_pong_tests):
        if test in dual_results:
            dual_min = dual_results[test].get('min_latency_us', 0)
            dual_max = dual_results[test].get('max_latency_us', 0)
            dual_avg = dual_results[test]['avg_latency_us']
            ax5.plot([i-0.1, i-0.1], [dual_min, dual_max], 'o-', color='#e74c3c', linewidth=2, markersize=6)
            ax5.plot(i-0.1, dual_avg, 's', color='#e74c3c', markersize=8)

        if test in single_results:
            single_min = single_results[test].get('min_latency_us', 0)
            single_max = single_results[test].get('max_latency_us', 0)
            single_avg = single_results[test]['avg_latency_us']
            ax5.plot([i+0.1, i+0.1], [single_min, single_max], 's-', color='#2ecc71', linewidth=2, markersize=6)
            ax5.plot(i+0.1, single_avg, 'o', color='#2ecc71', markersize=8)

    ax5.set_ylabel('Latency (μs)', fontsize=11, fontweight='bold')
    ax5.set_title('Min/Avg/Max Latency Range', fontsize=12, fontweight='bold')
    ax5.set_xticks(range(len(ping_pong_tests)))
    ax5.set_xticklabels([t.replace('Ping-Pong ', '') for t in ping_pong_tests], rotation=15, ha='right')
    ax5.grid(True, alpha=0.3)
    ax5.legend(['Dual (range)', 'Dual (avg)', 'Single (range)', 'Single (avg)'], loc='upper left', fontsize=8)

    # Plot 6: Percentile Distribution Comparison (Default payload)
    ax6 = plt.subplot(3, 3, 6)
    test_name = 'Ping-Pong (Default)'
    if test_name in dual_results and 'percentiles' in dual_results[test_name]:
        pcts = sorted(dual_results[test_name]['percentiles'].keys())
        dual_vals = [dual_results[test_name]['percentiles'][p] for p in pcts]
        ax6.plot(pcts, dual_vals, 'o-', label='Dual Board', color='#e74c3c', linewidth=2)

    if test_name in single_results and 'percentiles' in single_results[test_name]:
        pcts = sorted(single_results[test_name]['percentiles'].keys())
        single_vals = [single_results[test_name]['percentiles'][p] for p in pcts]
        ax6.plot(pcts, single_vals, 's-', label='Single Board', color='#2ecc71', linewidth=2)

    ax6.set_xlabel('Percentile', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Latency (μs)', fontsize=11, fontweight='bold')
    ax6.set_title('Percentile Distribution (Default Payload)', fontsize=12, fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    # Plot 7: Under Load Comparison
    ax7 = plt.subplot(3, 3, 7)
    under_load_metrics = ['avg_latency_us', 'jitter_us', 'min_latency_us', 'max_latency_us']
    metric_labels = ['Avg', 'Jitter', 'Min', 'Max']

    if 'Under Load' in dual_results and 'Under Load' in single_results:
        dual_vals = [dual_results['Under Load'].get(m, 0) for m in under_load_metrics]
        single_vals = [single_results['Under Load'].get(m, 0) for m in under_load_metrics]

        x_pos = np.arange(len(metric_labels))
        width = 0.35

        ax7.bar(x_pos - width/2, dual_vals, width, label='Dual Board', color='#e74c3c', alpha=0.8)
        ax7.bar(x_pos + width/2, single_vals, width, label='Single Board', color='#2ecc71', alpha=0.8)

        ax7.set_ylabel('Latency (μs)', fontsize=11, fontweight='bold')
        ax7.set_title('Under Load Performance (10k msg/sec)', fontsize=12, fontweight='bold')
        ax7.set_xticks(x_pos)
        ax7.set_xticklabels(metric_labels)
        ax7.legend()
        ax7.grid(True, alpha=0.3, axis='y')

    # Plot 8: Absolute Latency Difference (μs)
    ax8 = plt.subplot(3, 3, 8)
    differences = []
    for i, test in enumerate(ping_pong_tests):
        if test in dual_results and test in single_results:
            diff = dual_results[test]['avg_latency_us'] - single_results[test]['avg_latency_us']
            differences.append(diff)

    bars = ax8.bar(labels, differences, color='#3498db')
    ax8.set_ylabel('Latency Difference (μs)', fontsize=11, fontweight='bold')
    ax8.set_title('Absolute Latency Reduction (Dual - Single)', fontsize=12, fontweight='bold')
    ax8.grid(True, alpha=0.3, axis='y')

    for bar, val in zip(bars, differences):
        height = bar.get_height()
        ax8.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}',
                ha='center', va='bottom', fontweight='bold', fontsize=9)

    # Plot 9: Summary Comparison Table
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')

    summary_data = []
    for test in ping_pong_tests:
        if test in dual_results and test in single_results:
            dual_lat = dual_results[test]['avg_latency_us']
            single_lat = single_results[test]['avg_latency_us']
            improvement = ((dual_lat - single_lat) / dual_lat) * 100

            summary_data.append([
                test.replace('Ping-Pong ', ''),
                f"{dual_lat:.2f}",
                f"{single_lat:.2f}",
                f"{improvement:.1f}%"
            ])

    table = ax9.table(cellText=summary_data,
                     colLabels=['Test', 'Dual (μs)', 'Single (μs)', 'Improve'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.3, 0.23, 0.23, 0.24])

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Style header row
    for i in range(4):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Color improvement column
    for i in range(1, len(summary_data) + 1):
        for j in range(4):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#ecf0f1')
            if j == 3:  # Improvement column
                table[(i, j)].set_facecolor('#d5f4e6')

    ax9.set_title('Summary Comparison', fontsize=12, fontweight='bold', pad=20)

    plt.suptitle('LAN9662 Dual-Board vs Single-Board Performance Comparison\nComprehensive Network Performance Analysis',
                 fontsize=14, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('comparison_dual_vs_single.png', dpi=300, bbox_inches='tight')
    print("\n✓ Comparison visualization saved as comparison_dual_vs_single.png")

    # Generate detailed comparison report
    print("\n" + "="*80)
    print("LAN9662 DUAL-BOARD vs SINGLE-BOARD COMPARISON SUMMARY")
    print("="*80)

    print("\n📊 LATENCY COMPARISON:")
    print("-" * 80)
    print(f"{'Test':<20} {'Dual (μs)':<15} {'Single (μs)':<15} {'Improvement':<15}")
    print("-" * 80)

    for test in ping_pong_tests:
        if test in dual_results and test in single_results:
            dual_lat = dual_results[test]['avg_latency_us']
            single_lat = single_results[test]['avg_latency_us']
            improvement = ((dual_lat - single_lat) / dual_lat) * 100
            print(f"{test:<20} {dual_lat:<15.2f} {single_lat:<15.2f} {improvement:>13.1f}%")

    print("\n📉 JITTER COMPARISON:")
    print("-" * 80)
    print(f"{'Test':<20} {'Dual (μs)':<15} {'Single (μs)':<15} {'Improvement':<15}")
    print("-" * 80)

    for test in ping_pong_tests:
        if test in dual_results and test in single_results:
            dual_jit = dual_results[test]['jitter_us']
            single_jit = single_results[test]['jitter_us']
            improvement = ((dual_jit - single_jit) / dual_jit) * 100
            print(f"{test:<20} {dual_jit:<15.2f} {single_jit:<15.2f} {improvement:>13.1f}%")

    print("\n🔍 KEY FINDINGS:")
    print("-" * 80)

    # Calculate average improvement
    if 'Ping-Pong (Default)' in dual_results and 'Ping-Pong (Default)' in single_results:
        dual_avg = dual_results['Ping-Pong (Default)']['avg_latency_us']
        single_avg = single_results['Ping-Pong (Default)']['avg_latency_us']
        avg_improvement = ((dual_avg - single_avg) / dual_avg) * 100

        print(f"• Best Latency (Default Payload):")
        print(f"  - Dual Board:   {dual_avg:.2f} μs")
        print(f"  - Single Board: {single_avg:.2f} μs")
        print(f"  - Improvement:  {avg_improvement:.1f}%")
        print(f"  - Absolute Reduction: {dual_avg - single_avg:.2f} μs")

    print("\n• Throughput Performance:")
    if 'Throughput' in dual_results and 'Throughput' in single_results:
        dual_bw = dual_results['Throughput'].get('bandwidth_mbps', 0)
        single_bw = single_results['Throughput'].get('bandwidth_mbps', 0)
        print(f"  - Dual Board:   {dual_bw:.2f} Mbps")
        print(f"  - Single Board: {single_bw:.2f} Mbps")
        print(f"  - Difference:   {single_bw - dual_bw:.2f} Mbps")

if __name__ == '__main__':
    main()
