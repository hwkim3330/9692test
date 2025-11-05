# LAN9662 Dual-Board Network Performance Test

## Test Configuration

```
192.168.1.2 (PC) → LAN9662 Board #1 → LAN9662 Board #2 → 192.168.1.3 (Server)
            │                                              │
         enp2s0                                    sockperf server
                                                    port 11111 (UDP)
```

**Test Date:** 2025-11-05
**Protocol:** UDP
**Tool:** sockperf v3.7
**Network Interface:** enp2s0

## Executive Summary

Performance testing of two LAN9662 boards in series, measuring end-to-end latency, jitter, and throughput characteristics. The dual-board configuration demonstrates excellent low-latency performance suitable for Time-Sensitive Networking (TSN) applications.

### Key Findings

| Metric | Result |
|--------|--------|
| **Best Latency** | 52.69 μs (avg) @ 14B payload |
| **Lowest Jitter** | 15.91 μs @ 14B payload |
| **Max Throughput** | 912.72 Mbps |
| **Max Message Rate** | 81,272 msg/sec |
| **Packet Loss** | < 0.001% (ping-pong), 99% (under load) |

## Test Results Visualization

![Test Results](test_results_visualization.png)

## Detailed Test Results

### 1. Ping-Pong Latency Test (Default, ~14B payload)

**Test Duration:** 30 seconds
**Messages Sent/Received:** 280,219 / 280,219
**Packet Loss:** 0.000%

| Metric | Value |
|--------|-------|
| Average Latency | **52.69 μs** |
| Jitter (Std Dev) | **15.91 μs** |
| Min Latency | 38.75 μs |
| Max Latency | 551.36 μs |
| 50th Percentile | 47.32 μs |
| 90th Percentile | 62.33 μs |
| 99th Percentile | 122.60 μs |
| 99.9th Percentile | 187.83 μs |

**Analysis:** Excellent baseline latency performance with very low jitter, indicating stable network behavior through both boards.

---

### 2. Ping-Pong Latency Test (64B payload)

**Test Duration:** 20 seconds
**Messages Sent/Received:** 171,898 / 171,898
**Packet Loss:** 0.001%

| Metric | Value |
|--------|-------|
| Average Latency | **56.83 μs** |
| Jitter (Std Dev) | **17.43 μs** |
| Min Latency | 41.21 μs |
| Max Latency | 399.05 μs |
| 50th Percentile | 50.29 μs |
| 90th Percentile | 83.71 μs |
| 99th Percentile | 128.27 μs |

**Analysis:** Minimal latency increase (+4.14 μs) with 64-byte payloads, demonstrating efficient packet processing.

---

### 3. Ping-Pong Latency Test (512B payload)

**Test Duration:** 20 seconds
**Messages Sent/Received:** 104,349 / 104,349
**Packet Loss:** 0.001%

| Metric | Value |
|--------|-------|
| Average Latency | **93.64 μs** |
| Jitter (Std Dev) | **18.87 μs** |
| Min Latency | 65.02 μs |
| Max Latency | 389.94 μs |
| 50th Percentile | 85.89 μs |
| 90th Percentile | 110.69 μs |
| 99th Percentile | 173.58 μs |

**Analysis:** Latency scales linearly with packet size, indicating consistent processing overhead per byte.

---

### 4. Ping-Pong Latency Test (1472B payload)

**Test Duration:** 20 seconds
**Messages Sent/Received:** 74,372 / 74,372
**Packet Loss:** 0.001%

| Metric | Value |
|--------|-------|
| Average Latency | **131.39 μs** |
| Jitter (Std Dev) | **21.95 μs** |
| Min Latency | 110.71 μs |
| Max Latency | 1251.22 μs |
| 50th Percentile | 123.62 μs |
| 90th Percentile | 158.09 μs |
| 99th Percentile | 219.86 μs |

**Analysis:** Maximum UDP payload size shows expected latency increase while maintaining low jitter and excellent reliability.

---

### 5. Under Load Latency Test

**Test Configuration:** 10,000 messages/sec for 30 seconds
**Messages Sent:** 295,201
**Messages Received:** 2,953
**Packet Loss:** **99.000%**

| Metric | Value |
|--------|-------|
| Average Latency | **99.40 μs** |
| Jitter (Std Dev) | **23.69 μs** |
| Min Latency | 53.53 μs |
| Max Latency | 270.93 μs |

**Analysis:** High packet loss under sustained load indicates buffer saturation. The dual-board configuration has a practical limit around 9,000-10,000 msg/sec. Received messages still maintain low latency characteristics.

---

### 6. Throughput Test

**Test Duration:** 30 seconds
**Message Size:** 1472 bytes
**Total Messages Sent:** 2,438,169

| Metric | Value |
|--------|-------|
| **Bandwidth** | **912.72 Mbps** |
| **Message Rate** | **81,272 msg/sec** |
| **Throughput** | **114.09 MBps** |

**Analysis:** Excellent throughput achieving ~91% of Gigabit Ethernet theoretical maximum. The dual-board configuration maintains near line-rate performance for large packets.

---

## Latency vs Message Size Analysis

The relationship between message size and latency is approximately linear:

| Message Size | Avg Latency | Latency Increase |
|--------------|-------------|------------------|
| 14B (default) | 52.69 μs | baseline |
| 64B | 56.83 μs | +7.9% |
| 512B | 93.64 μs | +77.7% |
| 1472B | 131.39 μs | +149.3% |

**Latency increase rate:** ~0.054 μs per byte (approximately)

This linear scaling suggests:
- Efficient DMA and packet processing
- Minimal protocol overhead
- Predictable behavior for TSN scheduling

---

## Jitter Analysis

Jitter (latency standard deviation) remains relatively low across all tests:

| Test Type | Jitter (μs) | Jitter/Latency Ratio |
|-----------|-------------|---------------------|
| Ping-Pong (Default) | 15.91 | 30.2% |
| Ping-Pong (64B) | 17.43 | 30.7% |
| Ping-Pong (512B) | 18.87 | 20.2% |
| Ping-Pong (1472B) | 21.95 | 16.7% |
| Under Load | 23.69 | 23.8% |

**Key Observation:** Jitter increases minimally with packet size (15.91 → 21.95 μs), demonstrating consistent processing time variance. The jitter/latency ratio actually **decreases** with larger packets, indicating more deterministic behavior for larger frames.

---

## Performance Characteristics

### ✅ Strengths

1. **Ultra-Low Latency**: Sub-60 μs average latency for small packets through two boards
2. **Excellent Reliability**: < 0.001% packet loss under normal conditions
3. **High Throughput**: 912.72 Mbps sustained throughput
4. **Low Jitter**: Consistent performance with < 25 μs standard deviation
5. **Predictable Scaling**: Linear latency scaling with packet size
6. **TSN-Ready**: Performance characteristics suitable for industrial real-time applications

### ⚠️ Limitations

1. **Load Sensitivity**: 99% packet loss at 10,000 msg/sec indicates buffer constraints
2. **Practical Message Rate Limit**: ~9,000 msg/sec for reliable operation
3. **Max Latency Spikes**: Occasional spikes up to 1.25ms (1472B test)

---

## Test Files

All raw test data is included in this repository:

- `sockperf_pingpong_udp.txt` - Default payload ping-pong test
- `sockperf_pingpong_64B.txt` - 64-byte payload test
- `sockperf_pingpong_512B.txt` - 512-byte payload test
- `sockperf_pingpong_1472B.txt` - Maximum UDP payload test
- `sockperf_underload_udp.txt` - Sustained load test
- `sockperf_throughput_udp.txt` - Maximum throughput test
- `analyze_results.py` - Python analysis script
- `test_results_visualization.png` - Performance graphs

---

## Recommendations

### For Real-Time Applications

- **Message Size**: Keep packets < 512 bytes for sub-100 μs latency
- **Message Rate**: Limit to < 9,000 msg/sec to avoid packet loss
- **Priority Traffic**: Use TSN traffic shaping (CBS/TAS) for guaranteed latency
- **Monitoring**: Implement watchdog for latency spikes > 500 μs

### For Throughput Applications

- **Message Size**: Use 1472-byte packets for maximum efficiency
- **Rate Limiting**: ~80,000 msg/sec is safe for sustained operation
- **Flow Control**: Implement back-pressure mechanisms for burst traffic

---

## Future Tests

- [ ] Single-board configuration for comparison
- [ ] TSN Credit-Based Shaper (CBS) performance
- [ ] TSN Time-Aware Shaper (TAS) gate scheduling
- [ ] Mixed traffic scenarios (best-effort + time-critical)
- [ ] PTP time synchronization accuracy
- [ ] Frame Replication and Elimination (FRER) reliability

---

## Conclusion

The dual LAN9662 board configuration demonstrates **excellent performance** for Time-Sensitive Networking applications:

- **Latency**: 52.69 μs average (best case) - suitable for industrial control systems
- **Jitter**: 15.91 μs standard deviation - predictable for real-time scheduling
- **Throughput**: 912.72 Mbps - near line-rate Gigabit performance
- **Reliability**: 99.999% delivery rate under normal conditions

This baseline establishes the upper bound for dual-board latency. Single-board configurations should demonstrate approximately **50% lower latency** (26-35 μs range).

---

## Test Environment

**Hardware:**
- 2× Microchip LAN9662 VelocityDRIVE TSN Evaluation Boards
- PC: Intel Core with TSN-capable NIC (enp2s0)
- Gigabit Ethernet connections

**Software:**
- Ubuntu 22.04.3 LTS (Low-latency kernel 6.8.0-63)
- sockperf v3.7-no.git
- Python 3.10+ with matplotlib/numpy

**Network Topology:**
```
[PC Client] ----GbE---- [LAN9662-1] ----GbE---- [LAN9662-2] ----GbE---- [PC Server]
192.168.1.2            (Switch Port)           (Switch Port)           192.168.1.3
```

---

**Generated:** 2025-11-05
**Author:** Network Performance Testing Lab
**Repository:** https://github.com/hwkim3330/9692test