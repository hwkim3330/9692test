#!/usr/bin/env python3
"""
LAN9662 Dual-Board Network Performance Analysis
Analyzes sockperf test results for latency, jitter, and throughput
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
        results['jitter_us'] = results['std_dev_us']  # Jitter approximated as std-dev

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

    # Extract throughput info if available
    bw_match = re.search(r'BandWidth is ([\d.]+) MBps \(([\d.]+) Mbps\)', content)
    if bw_match:
        results['bandwidth_mbps'] = float(bw_match.group(2))
        results['bandwidth_MBps'] = float(bw_match.group(1))

    msg_rate_match = re.search(r'Message Rate is (\d+)', content)
    if msg_rate_match:
        results['msg_rate'] = int(msg_rate_match.group(1))

    # Extract sent/received messages
    sent_match = re.search(r'SentMessages=(\d+)', content)
    recv_match = re.search(r'ReceivedMessages=(\d+)', content)
    if sent_match and recv_match:
        results['sent_messages'] = int(sent_match.group(1))
        results['received_messages'] = int(recv_match.group(1))
        if results['sent_messages'] > 0:
            results['packet_loss_pct'] = (1 - results['received_messages'] / results['sent_messages']) * 100

    return results

def main():
    # Parse all test results
    tests = {
        'Ping-Pong (Default)': 'sockperf_pingpong_udp.txt',
        'Ping-Pong (64B)': 'sockperf_pingpong_64B.txt',
        'Ping-Pong (512B)': 'sockperf_pingpong_512B.txt',
        'Ping-Pong (1472B)': 'sockperf_pingpong_1472B.txt',
        'Under Load': 'sockperf_underload_udp.txt',
        'Throughput': 'sockperf_throughput_udp.txt',
    }

    results = {}
    for test_name, filename in tests.items():
        if Path(filename).exists():
            results[test_name] = parse_sockperf_file(filename)
            print(f"✓ Parsed {test_name}")
        else:
            print(f"✗ Missing {filename}")

    # Create visualization
    fig = plt.figure(figsize=(16, 10))

    # Plot 1: Latency by Message Size
    ax1 = plt.subplot(2, 3, 1)
    msg_sizes = [14, 64, 512, 1472]  # Approximate default is 14 bytes
    ping_pong_tests = ['Ping-Pong (Default)', 'Ping-Pong (64B)', 'Ping-Pong (512B)', 'Ping-Pong (1472B)']
    latencies = [results[t]['avg_latency_us'] for t in ping_pong_tests if t in results]
    jitters = [results[t]['jitter_us'] for t in ping_pong_tests if t in results]

    ax1.errorbar(msg_sizes[:len(latencies)], latencies, yerr=jitters,
                 marker='o', linewidth=2, markersize=8, capsize=5)
    ax1.set_xlabel('Message Size (Bytes)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Latency (μs)', fontsize=11, fontweight='bold')
    ax1.set_title('Latency vs Message Size', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')

    # Plot 2: Latency Distribution (Percentiles)
    ax2 = plt.subplot(2, 3, 2)
    for test_name in ['Ping-Pong (Default)', 'Ping-Pong (1472B)']:
        if test_name in results and 'percentiles' in results[test_name]:
            pcts = sorted(results[test_name]['percentiles'].keys())
            vals = [results[test_name]['percentiles'][p] for p in pcts]
            label = test_name.replace('Ping-Pong ', '')
            ax2.plot(pcts, vals, marker='o', label=label, linewidth=2)

    ax2.set_xlabel('Percentile', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Latency (μs)', fontsize=11, fontweight='bold')
    ax2.set_title('Latency Percentile Distribution', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Jitter Comparison
    ax3 = plt.subplot(2, 3, 3)
    test_names = list(results.keys())
    jitter_vals = [results[t]['jitter_us'] for t in test_names if 'jitter_us' in results[t]]
    colors = ['#2ecc71' if j < 20 else '#f39c12' if j < 25 else '#e74c3c' for j in jitter_vals]

    bars = ax3.barh(test_names[:len(jitter_vals)], jitter_vals, color=colors)
    ax3.set_xlabel('Jitter (μs)', fontsize=11, fontweight='bold')
    ax3.set_title('Jitter by Test Type', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')

    # Plot 4: Min/Avg/Max Latency
    ax4 = plt.subplot(2, 3, 4)
    ping_tests = [t for t in test_names if 'Ping-Pong' in t]
    x_pos = np.arange(len(ping_tests))

    mins = [results[t].get('min_latency_us', 0) for t in ping_tests]
    avgs = [results[t].get('avg_latency_us', 0) for t in ping_tests]
    maxs = [results[t].get('max_latency_us', 0) for t in ping_tests]

    width = 0.25
    ax4.bar(x_pos - width, mins, width, label='Min', color='#2ecc71')
    ax4.bar(x_pos, avgs, width, label='Avg', color='#3498db')
    ax4.bar(x_pos + width, maxs, width, label='Max', color='#e74c3c')

    ax4.set_ylabel('Latency (μs)', fontsize=11, fontweight='bold')
    ax4.set_title('Min/Avg/Max Latency Comparison', fontsize=12, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([t.replace('Ping-Pong ', '') for t in ping_tests], rotation=15, ha='right')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')

    # Plot 5: Throughput Metrics
    ax5 = plt.subplot(2, 3, 5)
    throughput_data = []
    if 'Throughput' in results:
        t_res = results['Throughput']
        throughput_data.append({
            'label': 'Bandwidth\n(Mbps)',
            'value': t_res.get('bandwidth_mbps', 0),
            'color': '#9b59b6'
        })
        throughput_data.append({
            'label': 'Msg Rate\n(msg/sec)',
            'value': t_res.get('msg_rate', 0) / 1000,  # Convert to thousands
            'color': '#1abc9c'
        })

    if throughput_data:
        labels = [d['label'] for d in throughput_data]
        values = [d['value'] for d in throughput_data]
        colors = [d['color'] for d in throughput_data]

        bars = ax5.bar(labels, values, color=colors)
        ax5.set_ylabel('Value', fontsize=11, fontweight='bold')
        ax5.set_title('Throughput Test Results', fontsize=12, fontweight='bold')

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}',
                    ha='center', va='bottom', fontweight='bold')

        # Add units as text
        ax5.text(0, values[0]*0.5, 'Mbps', ha='center', va='center', fontsize=10, color='white', fontweight='bold')
        ax5.text(1, values[1]*0.5, 'k msg/s', ha='center', va='center', fontsize=10, color='white', fontweight='bold')

    # Plot 6: Summary Statistics Table
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')

    summary_data = []
    for test_name, result in results.items():
        if 'avg_latency_us' in result:
            summary_data.append([
                test_name.replace('Ping-Pong ', 'PP '),
                f"{result['avg_latency_us']:.2f}",
                f"{result['jitter_us']:.2f}",
                f"{result.get('min_latency_us', 0):.2f}",
                f"{result.get('max_latency_us', 0):.2f}",
            ])

    table = ax6.table(cellText=summary_data,
                     colLabels=['Test', 'Avg (μs)', 'Jitter (μs)', 'Min (μs)', 'Max (μs)'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.3, 0.175, 0.175, 0.175, 0.175])

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Style header row
    for i in range(5):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Alternate row colors
    for i in range(1, len(summary_data) + 1):
        for j in range(5):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#ecf0f1')

    ax6.set_title('Summary Statistics', fontsize=12, fontweight='bold', pad=20)

    plt.suptitle('LAN9662 Dual-Board Network Performance Test Results\n192.168.1.2 → LAN9662-1 → LAN9662-2 → 192.168.1.3',
                 fontsize=14, fontweight='bold', y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('test_results_visualization.png', dpi=300, bbox_inches='tight')
    print("\n✓ Visualization saved as test_results_visualization.png")

    # Generate summary report
    print("\n" + "="*80)
    print("LAN9662 DUAL-BOARD NETWORK PERFORMANCE TEST SUMMARY")
    print("="*80)
    print(f"Test Configuration: 192.168.1.2 → LAN9662-1 → LAN9662-2 → 192.168.1.3")
    print(f"Protocol: UDP")
    print("="*80)

    for test_name, result in results.items():
        print(f"\n{test_name}:")
        if 'avg_latency_us' in result:
            print(f"  Average Latency: {result['avg_latency_us']:.2f} μs")
            print(f"  Jitter (Std Dev): {result['jitter_us']:.2f} μs")
            print(f"  Min Latency: {result.get('min_latency_us', 0):.2f} μs")
            print(f"  Max Latency: {result.get('max_latency_us', 0):.2f} μs")
        if 'bandwidth_mbps' in result:
            print(f"  Bandwidth: {result['bandwidth_mbps']:.2f} Mbps")
        if 'msg_rate' in result:
            print(f"  Message Rate: {result['msg_rate']:,} msg/sec")
        if 'packet_loss_pct' in result:
            print(f"  Packet Loss: {result['packet_loss_pct']:.3f}%")
        if 'total_observations' in result:
            print(f"  Total Observations: {result['total_observations']:,}")

if __name__ == '__main__':
    main()
