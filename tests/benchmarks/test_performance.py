import time
import psutil
import pytest
from src.core.controllers.container import ServiceContainer

class TestPerformanceBenchmarks:
    def test_container_initialization_latency(self):
        start = time.time()
        container = ServiceContainer.get_instance()
        elapsed = time.time() - start

        # Initialization must take < 0.5s
        assert elapsed < 0.5
        assert container.device_state_service.get_current_state() is not None

    def test_timeline_write_throughput(self):
        container = ServiceContainer.get_instance()
        start = time.time()

        # Write 50 events rapidly
        for i in range(50):
            container.timeline_service.record_event("BENCHMARK_EVENT", "INFO", f"Benchmark iteration {i}")

        elapsed = time.time() - start
        avg_latency_ms = (elapsed / 50) * 1000

        # Average write latency must be < 25ms per event on Windows SQLite
        assert avg_latency_ms < 25.0

    def test_memory_footprint(self):
        proc = psutil.Process()
        mem_mb = proc.memory_info().rss / (1024 * 1024)

        # Baseline RAM footprint must be < 150MB
        assert mem_mb < 150.0
