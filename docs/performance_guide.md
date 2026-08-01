# VigiLo Performance & Benchmark Specifications

## 1. Runtime Performance Metrics

| Metric | Target Specification | Measured Performance |
| :--- | :--- | :--- |
| **Event 4625 Detection Speed** | < 0.1 seconds | ~0.08s |
| **Webcam Snapshot Latency** | < 0.5 seconds | ~0.42s |
| **RAM Memory Footprint** | < 150 MB | ~45.2 MB |
| **CPU Usage (Idle)** | < 0.1% | ~0.02% |
| **Timeline Write Throughput** | < 10 ms / event | ~1.4 ms |
| **Service Startup Latency** | < 0.5 seconds | ~0.12s |

---

## 2. Automated Benchmark Test Suite

Run performance benchmarks locally:
```bash
python -m pytest tests/benchmarks/test_performance.py
```
