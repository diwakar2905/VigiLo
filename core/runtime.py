# core/runtime.py
import threading
import time
import os
from abc import ABC, abstractmethod
from logs.logger import logger

# Try importing psutil for runtime metrics
try:
    import psutil
except ImportError:
    psutil = None

# 1. Runtime Exceptions
class RuntimeError(Exception):
    pass

class ServiceInitError(RuntimeError):
    pass

class ServiceStateError(RuntimeError):
    pass

# 2. Advanced Lifecycle Status Levels
class HealthLevel:
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"

# 3. IService Interface
class IService(ABC):
    @property
    def dependencies(self) -> list:
        """Returns list of service names this service depends on."""
        return []

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def start(self) -> bool:
        pass

    @abstractmethod
    def stop(self) -> bool:
        pass

    @abstractmethod
    def restart(self) -> bool:
        pass

    @abstractmethod
    def health(self) -> bool:
        pass

    @abstractmethod
    def status(self) -> str:
        pass

# 4. Managed Thread Helper (Cooperative loops, non-daemon)
class ManagedThread:
    def __init__(self, target, name: str, args=(), kwargs=None):
        self.target = target
        self.name = name
        self.args = args
        self.kwargs = kwargs or {}
        self.stop_event = threading.Event()
        self._thread = None

    def start(self):
        self.stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name=self.name,
            daemon=False # Explicitly managed thread
        )
        self._thread.start()

    def _run(self):
        try:
            self.target(self.stop_event, *self.args, **self.kwargs)
        except Exception as e:
            logger.error(f"ManagedThread '{self.name}' crashed: {e}")

    def stop(self, timeout: float = 5.0):
        self.stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning(f"ManagedThread '{self.name}' did not stop gracefully within {timeout}s.")

# 5. Internal Pub-Sub Lifecycle Event Publisher
class EventPublisher:
    def __init__(self):
        self._listeners = []
        self._lock = threading.Lock()

    def subscribe(self, callback):
        with self._lock:
            self._listeners.append(callback)

    def publish(self, event_type: str, service_name: str, details: str = ""):
        event = {
            "event_type": event_type,
            "service_name": service_name,
            "timestamp": time.time(),
            "details": details
        }
        with self._lock:
            for listener in self._listeners:
                try:
                    listener(event)
                except Exception as e:
                    logger.error(f"EventPublisher callback exception: {e}")

# Global internal broker instance
event_broker = EventPublisher()

# 6. Service Manager with Dependency Resolution & Metrics
class ServiceManager:
    def __init__(self):
        self._services = {}
        self._states = {}
        self._failure_counts = {}
        self._backoff_delays = {}
        self._last_restart_time = {}
        self._metrics = {}
        self._lock = threading.Lock()

    def register_service(self, name: str, service: IService):
        with self._lock:
            if name in self._services:
                raise ServiceStateError(f"Service {name} is already registered.")
            self._services[name] = service
            self._states[name] = HealthLevel.OFFLINE
            self._failure_counts[name] = 0
            self._backoff_delays[name] = 1.0 # Start backoff delay at 1s
            self._last_restart_time[name] = 0.0
            self._metrics[name] = {
                "restart_count": 0,
                "uptime": 0.0,
                "error_count": 0,
                "cpu_usage": 0.0,
                "memory_usage_mb": 0.0
            }
            logger.info(f"ServiceManager: Registered service '{name}'.")

    def _get_start_order(self) -> list:
        """Topological sort using depth-first search (DFS) to resolve launch dependencies."""
        visited = set()
        temp_visited = set()
        order = []

        def visit(name):
            if name in temp_visited:
                raise RuntimeError(f"Circular dependency detected involving service '{name}'.")
            if name not in visited:
                temp_visited.add(name)
                # Ensure dependencies are registered
                if name in self._services:
                    for dep in self._services[name].dependencies:
                        visit(dep)
                temp_visited.remove(name)
                visited.add(name)
                order.append(name)

        for service_name in self._services:
            if service_name not in visited:
                visit(service_name)
        return order

    def initialize_all(self) -> bool:
        start_order = self._get_start_order()
        for name in start_order:
            svc = self._services[name]
            logger.info(f"ServiceManager: Initializing '{name}'...")
            try:
                if not svc.initialize():
                    self._states[name] = HealthLevel.CRITICAL
                    event_broker.publish("ServiceFailed", name, "Initialization failed")
                    return False
                self._states[name] = HealthLevel.WARNING
            except Exception as e:
                self._states[name] = HealthLevel.CRITICAL
                event_broker.publish("ServiceFailed", name, f"Init crash: {e}")
                return False
        return True

    def start_all(self):
        start_order = self._get_start_order()
        for name in start_order:
            if self._states[name] == HealthLevel.CRITICAL:
                continue
            svc = self._services[name]
            try:
                if svc.start():
                    self._states[name] = HealthLevel.HEALTHY
                    self._metrics[name]["start_time"] = time.time()
                    event_broker.publish("ServiceStarted", name)
                else:
                    self._states[name] = HealthLevel.CRITICAL
                    event_broker.publish("ServiceFailed", name, "Start method returned False")
            except Exception as e:
                self._states[name] = HealthLevel.CRITICAL
                event_broker.publish("ServiceFailed", name, f"Start exception: {e}")

    def stop_all(self):
        # Stop in reverse order of initialization (leaves dependencies alive until callers exit)
        stop_order = reversed(self._get_start_order())
        for name in stop_order:
            svc = self._services[name]
            try:
                svc.stop()
                self._states[name] = HealthLevel.OFFLINE
                event_broker.publish("ServiceStopped", name)
            except Exception as e:
                logger.error(f"ServiceManager: Error stopping service '{name}': {e}")

    def check_health(self) -> dict:
        health_report = {}
        with self._lock:
            # Query process resource usage metrics
            proc_cpu = 0.0
            proc_mem = 0.0
            if psutil:
                try:
                    p = psutil.Process(os.getpid())
                    proc_cpu = p.cpu_percent()
                    proc_mem = p.memory_info().rss / (1024 * 1024) # MB
                except Exception:
                    pass

            for name, svc in self._services.items():
                try:
                    is_healthy = svc.health()
                    
                    # Update live runtime stats metrics
                    self._metrics[name]["cpu_usage"] = proc_cpu
                    self._metrics[name]["memory_usage_mb"] = proc_mem
                    if "start_time" in self._metrics[name]:
                        self._metrics[name]["uptime"] = time.time() - self._metrics[name]["start_time"]

                    if is_healthy:
                        self._states[name] = HealthLevel.HEALTHY
                        health_report[name] = True
                    else:
                        self._states[name] = HealthLevel.DEGRADED
                        health_report[name] = False
                except Exception as e:
                    self._states[name] = HealthLevel.CRITICAL
                    self._metrics[name]["error_count"] += 1
                    health_report[name] = False
        return health_report

    def restart_service(self, name: str):
        with self._lock:
            if name not in self._services:
                return

            # Apply backoff progression delay (1s -> 2s -> 5s -> 10s -> 30s -> Critical Failure)
            delay = self._backoff_delays[name]
            logger.warning(f"ServiceManager: Applying backoff delay of {delay}s before restarting '{name}'...")
            time.sleep(delay)

            # Update backoff ladder
            if delay < 2.0:
                self._backoff_delays[name] = 2.0
            elif delay < 5.0:
                self._backoff_delays[name] = 5.0
            elif delay < 10.0:
                self._backoff_delays[name] = 10.0
            elif delay < 30.0:
                self._backoff_delays[name] = 30.0
            else:
                # Exceeded critical threshold failure count
                self._states[name] = HealthLevel.CRITICAL
                event_broker.publish("ServiceFailed", name, "Backoff threshold exceeded")
                logger.error(f"ServiceManager: Service '{name}' transitioned to CRITICAL failure state. Restarts suspended.")
                return

            self._metrics[name]["restart_count"] += 1
            event_broker.publish("ServiceRestarted", name, f"Retry attempt: {self._metrics[name]['restart_count']}")

            try:
                self._services[name].restart()
                self._states[name] = HealthLevel.HEALTHY
                self._failure_counts[name] = 0
                self._backoff_delays[name] = 1.0 # Reset backoff delay on successful recovery
                self._metrics[name]["start_time"] = time.time()
                event_broker.publish("ServiceRecovered", name)
                logger.info(f"ServiceManager: Service '{name}' successfully recovered.")
            except Exception as e:
                self._states[name] = HealthLevel.CRITICAL
                self._metrics[name]["error_count"] += 1
                logger.error(f"ServiceManager: Restart attempt on '{name}' crashed: {e}")

    def query_metrics(self, name: str) -> dict:
        """Returns the current runtime metrics for a specific service."""
        with self._lock:
            if name in self._metrics:
                metrics_copy = dict(self._metrics[name])
                metrics_copy["state"] = self._states[name]
                return metrics_copy
            return {}

# 7. Thread Supervisor Watchdog
class ThreadSupervisor:
    def __init__(self, service_manager: ServiceManager):
        self.sm = service_manager
        self.stop_event = threading.Event()
        self._watchdog_thread = None

    def start(self):
        # Starts watchdog as a standard managed thread loop
        self.stop_event.clear()
        self._watchdog_thread = threading.Thread(target=self._supervise, name="RuntimeWatchdog", daemon=False)
        self._watchdog_thread.start()
        logger.info("Runtime: Thread supervisor active.")

    def stop(self):
        self.stop_event.set()
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=5)

    def _supervise(self):
        while not self.stop_event.is_set():
            time.sleep(10)
            report = self.sm.check_health()
            for name, is_healthy in report.items():
                if not is_healthy:
                    logger.warning(f"Runtime: Watchdog detected failed state on '{name}'!")
                    self.sm.restart_service(name)
