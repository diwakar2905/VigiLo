# core/runtime.py
import threading
import time
import os
import sys
import uuid
from abc import ABC, abstractmethod
from logs.logger import logger

# Try importing psutil for resource metric retrieval
try:
    import psutil
except ImportError:
    psutil = None

# ==========================================
# 1. Structured Runtime Exceptions
# ==========================================
class VigiLoRuntimeException(Exception):
    """Base exception for all runtime-related errors."""
    pass

class ServiceInitializationException(VigiLoRuntimeException):
    """Raised when service pre-flight initialization fails."""
    pass

class ServiceCrashException(VigiLoRuntimeException):
    """Raised when a service throws an unhandled crash during runtime."""
    pass

class HeartbeatTimeoutException(VigiLoRuntimeException):
    """Raised when a service misses its heartbeat deadline limit."""
    pass

class RestartLimitExceededException(VigiLoRuntimeException):
    """Raised when a service exceeds its restart policy retries limit."""
    pass

class ShutdownTimeoutException(VigiLoRuntimeException):
    """Raised when a service fails to exit cleanly on shutdown."""
    pass

# ==========================================
# 2. Lifecycle States Enumeration
# ==========================================
class LifecycleState:
    CREATED = "Created"
    INITIALIZED = "Initialized"
    STARTING = "Starting"
    RUNNING = "Running"
    PAUSED = "Paused"
    STOPPING = "Stopping"
    STOPPED = "Stopped"
    RESTARTING = "Restarting"
    FAILED = "Failed"
    DISPOSED = "Disposed"

# ==========================================
# 3. IService Interface Definition
# ==========================================
class IService(ABC):
    @property
    def dependencies(self) -> list:
        """Returns list of service names this service depends on."""
        return []

    @abstractmethod
    def initialize(self) -> bool:
        """Runs pre-flight setup checks."""
        pass

    @abstractmethod
    def start(self) -> bool:
        """Starts the service thread execution."""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """Stops the service execution loop."""
        pass

    @abstractmethod
    def restart(self) -> bool:
        """Restarts the service cleanly."""
        pass

    @abstractmethod
    def pause(self) -> bool:
        """Temporarily pauses service loop actions."""
        pass

    @abstractmethod
    def resume(self) -> bool:
        """Resumes paused service actions."""
        pass

    @abstractmethod
    def health(self) -> bool:
        """Returns True if the service thread is alive and healthy."""
        pass

    @abstractmethod
    def status(self) -> str:
        """Returns the current LifecycleState string."""
        pass

    @abstractmethod
    def dispose(self) -> None:
        """Releases system file handles and hardware locks."""
        pass

# ==========================================
# 4. Managed Worker Thread (Cooperative Cancellation)
# ==========================================
class ManagedThread:
    def __init__(self, target, name: str, args=(), kwargs=None):
        self.target = target
        self.name = name
        self.args = args
        self.kwargs = kwargs or {}
        self.stop_event = threading.Event()
        self._thread = None
        self._correlation_id = str(uuid.uuid4())

    def start(self):
        self.stop_event.clear()
        # Non-daemon thread structure, explicitly joined on lifecycle stop
        self._thread = threading.Thread(
            target=self._run,
            name=self.name,
            daemon=False
        )
        self._thread.start()

    def _run(self):
        start_time = time.time()
        logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Runtime] Thread: {self.name} | Action: Start | CorrelationID: {self._correlation_id}")
        try:
            self.target(self.stop_event, *self.args, **self.kwargs)
            duration = time.time() - start_time
            logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Runtime] Thread: {self.name} | Action: Completed | Duration: {duration:.2f}s | CorrelationID: {self._correlation_id}")
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Runtime] Thread: {self.name} | Action: Crash | Error: {e} | Duration: {duration:.2f}s | CorrelationID: {self._correlation_id}")

    def stop(self, timeout: float = 5.0) -> bool:
        self.stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Runtime] Thread: {self.name} failed to stop gracefully in {timeout}s.")
                return False
        return True

# ==========================================
# 5. Internal Pub-Sub Event Publisher
# ==========================================
class EventPublisher:
    def __init__(self):
        self._listeners = []
        self._lock = threading.Lock()

    def subscribe(self, callback):
        with self._lock:
            self._listeners.append(callback)

    def publish(self, event_type: str, service_name: str, details: str = ""):
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "service_name": service_name,
            "details": details,
            "correlation_id": str(uuid.uuid4())
        }
        with self._lock:
            for listener in self._listeners:
                try:
                    listener(event)
                except Exception as e:
                    logger.error(f"EventPublisher callback exception: {e}")

# Global internal broker instance
event_broker = EventPublisher()

# ==========================================
# 6. Service Manager & Lifecycle Manager
# ==========================================
class ServiceManager:
    _instance = None
    _singleton_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._singleton_lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
            return cls._instance

    def __init__(self):
        # Prevent re-initialization if already initialized
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._services = {}
        self._states = {}
        self._dependencies = {}
        self._failure_counts = {}
        self._backoff_delays = {}
        self._last_heartbeats = {}
        self._metrics = {}
        self._lock = threading.Lock()
        self._initialized = True

    def register_service(self, name: str, service: IService):
        with self._lock:
            if name in self._services:
                raise ServiceInitializationException(f"Service '{name}' already registered.")
            self._services[name] = service
            self._states[name] = LifecycleState.CREATED
            self._dependencies[name] = service.dependencies
            self._failure_counts[name] = 0
            self._backoff_delays[name] = 1.0 # 1 second initial delay
            self._last_heartbeats[name] = time.time()
            self._metrics[name] = {
                "restart_count": 0,
                "uptime": 0.0,
                "error_count": 0,
                "cpu_usage": 0.0,
                "memory_usage_mb": 0.0,
                "queue_length": 0,
                "last_activity": time.time()
            }
            logger.info(f"ServiceManager: Registered service '{name}'.")

    def lookup_service(self, name: str) -> IService:
        with self._lock:
            return self._services.get(name)

    def _resolve_dependencies(self) -> list:
        """Topological sort using depth-first search to resolve build dependency graphs."""
        visited = set()
        temp_visited = set()
        order = []

        def visit(name):
            if name in temp_visited:
                raise VigiLoRuntimeException(f"Circular dependency detected involving service '{name}'.")
            if name not in visited:
                temp_visited.add(name)
                # Walk child dependencies
                for dep in self._dependencies.get(name, []):
                    visit(dep)
                temp_visited.remove(name)
                visited.add(name)
                order.append(name)

        for service_name in self._services:
            if service_name not in visited:
                visit(service_name)
        return order

    def initialize_all(self) -> bool:
        order = self._resolve_dependencies()
        for name in order:
            logger.info(f"ServiceManager: Initializing '{name}'...")
            svc = self._services[name]
            self._states[name] = LifecycleState.INITIALIZED
            try:
                if not svc.initialize():
                    self._states[name] = LifecycleState.FAILED
                    event_broker.publish("ServiceFailed", name, "Initialization failed")
                    return False
            except Exception as e:
                self._states[name] = LifecycleState.FAILED
                event_broker.publish("ServiceFailed", name, f"Init crash: {e}")
                return False
        return True

    def start_all(self):
        order = self._resolve_dependencies()
        for name in order:
            svc = self._services[name]
            self._states[name] = LifecycleState.STARTING
            try:
                if svc.start():
                    self._states[name] = LifecycleState.RUNNING
                    self._metrics[name]["start_time"] = time.time()
                    event_broker.publish("ServiceStarted", name)
                else:
                    self._states[name] = LifecycleState.FAILED
                    event_broker.publish("ServiceFailed", name, "Start returned False")
            except Exception as e:
                self._states[name] = LifecycleState.FAILED
                event_broker.publish("ServiceFailed", name, f"Start exception: {e}")

    def stop_all(self, timeout: float = 5.0):
        # Stop in reverse order of initialization
        order = reversed(self._resolve_dependencies())
        event_broker.publish("ShutdownStarted", "RuntimeHost")
        for name in order:
            svc = self._services[name]
            self._states[name] = LifecycleState.STOPPING
            try:
                svc.stop()
                svc.dispose()
                self._states[name] = LifecycleState.STOPPED
                event_broker.publish("ServiceStopped", name)
            except Exception as e:
                logger.error(f"ServiceManager: Error during shutdown of '{name}': {e}")
                self._states[name] = LifecycleState.FAILED
        event_broker.publish("ShutdownCompleted", "RuntimeHost")

    def publish_heartbeat(self, name: str):
        with self._lock:
            if name in self._last_heartbeats:
                self._last_heartbeats[name] = time.time()
                if name in self._metrics:
                    self._metrics[name]["last_activity"] = time.time()

    def get_service_metrics(self, name: str) -> dict:
        with self._lock:
            if name in self._metrics:
                metrics_copy = dict(self._metrics[name])
                metrics_copy["state"] = self._states[name]
                metrics_copy["heartbeat_delay"] = time.time() - self._last_heartbeats.get(name, time.time())
                return metrics_copy
            return {}
            
    def query_global_metrics(self) -> dict:
        with self._lock:
            total = len(self._services)
            healthy = sum(1 for s in self._states.values() if s == LifecycleState.RUNNING)
            failed = sum(1 for s in self._states.values() if s == LifecycleState.FAILED)
            
            proc_cpu = 0.0
            proc_mem = 0.0
            if psutil:
                try:
                    p = psutil.Process(os.getpid())
                    proc_cpu = p.cpu_percent()
                    proc_mem = p.memory_info().rss / (1024 * 1024)
                except Exception:
                    pass

            return {
                "total_services": total,
                "healthy_services": healthy,
                "failed_services": failed,
                "system_cpu_usage": proc_cpu,
                "system_memory_mb": proc_mem
            }

# ==========================================
# 7. Restart Policies Engine & SRE Supervisor
# ==========================================
class ThreadSupervisor:
    def __init__(self, service_manager: ServiceManager, max_restarts: int = 5):
        self.sm = service_manager
        self.max_restarts = max_restarts
        self.stop_event = threading.Event()
        self._watchdog_thread = None

    def start(self):
        self.stop_event.clear()
        self._watchdog_thread = threading.Thread(
            target=self._supervise,
            name="SRE_Watchdog_Supervisor",
            daemon=False
        )
        self._watchdog_thread.start()

    def stop(self):
        self.stop_event.set()
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=5)

    def _supervise(self):
        logger.info("Runtime: ThreadSupervisor watchdog loop started.")
        while not self.stop_event.is_set():
            time.sleep(10)
            
            # Check heartbeats and service health
            for name, svc in list(self.sm._services.items()):
                try:
                    # 1. Verify health hook check
                    is_healthy = svc.health()
                except Exception:
                    is_healthy = False

                # 2. Verify Heartbeat Check (Timeout > 30 seconds triggers recovery)
                last_hb = self.sm._last_heartbeats.get(name, time.time())
                if time.time() - last_hb > 30.0:
                    logger.warning(f"Runtime: Heartbeat timeout detected on service '{name}'.")
                    event_broker.publish("HeartbeatLost", name)
                    is_healthy = False

                if not is_healthy:
                    self._recover_service(name)

    def _recover_service(self, name: str):
        # Enforce restart limits and delays
        restarts = self.sm._metrics[name]["restart_count"]
        if restarts >= self.max_restarts:
            self.sm._states[name] = LifecycleState.FAILED
            logger.error(f"Runtime: Service '{name}' exceeded critical restart limit ({self.max_restarts}). Restarts suspended.")
            event_broker.publish("ServiceFailed", name, "Restart limit exceeded")
            return

        delay = self.sm._backoff_delays[name]
        logger.info(f"Runtime: Recovering '{name}'. Applying backoff delay of {delay}s...")
        time.sleep(delay)

        # Exponential backoff progression (1s -> 2s -> 5s -> 10s -> 30s)
        if delay < 2.0:
            self.sm._backoff_delays[name] = 2.0
        elif delay < 5.0:
            self.sm._backoff_delays[name] = 5.0
        elif delay < 10.0:
            self.sm._backoff_delays[name] = 10.0
        elif delay < 30.0:
            self.sm._backoff_delays[name] = 30.0

        self.sm._metrics[name]["restart_count"] += 1
        self.sm._states[name] = LifecycleState.RESTARTING
        event_broker.publish("ServiceRestarted", name)

        try:
            svc = self.sm._services[name]
            svc.restart()
            self.sm._states[name] = LifecycleState.RUNNING
            self.sm._last_heartbeats[name] = time.time()
            self.sm._backoff_delays[name] = 1.0 # Reset backoff on recovery success
            logger.info(f"Runtime: Service '{name}' recovered successfully.")
        except Exception as e:
            logger.critical(f"Runtime: Recovery restart failed for '{name}': {e}")
            self.sm._states[name] = LifecycleState.FAILED

# ==========================================
# 8. Runtime Host Facade Entry Point
# ==========================================
class RuntimeHost:
    def __init__(self):
        self.service_manager = ServiceManager()
        self.supervisor = ThreadSupervisor(self.service_manager)

    def register(self, name: str, service: IService):
        self.service_manager.register_service(name, service)

    def startup(self) -> bool:
        logger.info("RuntimeHost: Launching pre-flight boot procedures...")
        if not self.service_manager.initialize_all():
            logger.critical("RuntimeHost: Pre-flight initialization failed. Halting boot sequence.")
            return False
            
        self.service_manager.start_all()
        self.supervisor.start()
        logger.info("RuntimeHost: Application started successfully.")
        return True

    def shutdown(self, timeout: float = 5.0):
        logger.info("RuntimeHost: Executing graceful shutdown sequence...")
        self.supervisor.stop()
        self.service_manager.stop_all(timeout)
        logger.info("RuntimeHost: Shutdown sequence completed.")
