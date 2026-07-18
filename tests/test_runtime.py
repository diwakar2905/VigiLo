# tests/test_runtime.py
import unittest
from core.runtime import (
    IService,
    LifecycleState,
    ServiceManager,
    ThreadSupervisor,
    VigiLoRuntimeException,
)


class MockService(IService):
    def __init__(self, name: str, dependencies=None):
        self.name = name
        self._dependencies = dependencies or []
        self._state = LifecycleState.CREATED
        self._initialized = False
        self._started = False
        self._healthy = True

    @property
    def dependencies(self) -> list:
        return self._dependencies

    def initialize(self) -> bool:
        self._initialized = True
        self._state = LifecycleState.INITIALIZED
        return True

    def start(self) -> bool:
        self._started = True
        self._state = LifecycleState.RUNNING
        return True

    def stop(self) -> bool:
        self._started = False
        self._state = LifecycleState.STOPPED
        return True

    def restart(self) -> bool:
        self.stop()
        return self.start()

    def pause(self) -> bool:
        self._state = LifecycleState.PAUSED
        return True

    def resume(self) -> bool:
        self._state = LifecycleState.RUNNING
        return True

    def health(self) -> bool:
        return self._healthy

    def status(self) -> str:
        return self._state

    def dispose(self) -> None:
        self._state = LifecycleState.DISPOSED


class TestRuntimeOrchestration(unittest.TestCase):
    def setUp(self):
        # ServiceManager is a singleton, so clear its internal dictionary for isolation
        self.sm = ServiceManager()
        self.sm._services.clear()
        self.sm._states.clear()
        self.sm._dependencies.clear()
        self.sm._failure_counts.clear()
        self.sm._backoff_delays.clear()
        self.sm._last_heartbeats.clear()
        self.sm._metrics.clear()

    def test_dependency_resolution_topological(self):
        # Register services out of order
        svc_a = MockService("ServiceA", dependencies=["ServiceB"])
        svc_b = MockService("ServiceB")

        self.sm.register_service("ServiceA", svc_a)
        self.sm.register_service("ServiceB", svc_b)

        order = self.sm._resolve_dependencies()
        self.assertEqual(order, ["ServiceB", "ServiceA"])

    def test_circular_dependency_check(self):
        svc_a = MockService("ServiceA", dependencies=["ServiceB"])
        svc_b = MockService("ServiceB", dependencies=["ServiceA"])

        self.sm.register_service("ServiceA", svc_a)
        self.sm.register_service("ServiceB", svc_b)

        with self.assertRaises(VigiLoRuntimeException):
            self.sm._resolve_dependencies()

    def test_lifecycle_transitions(self):
        svc = MockService("TestService")
        self.sm.register_service("TestService", svc)

        self.assertTrue(self.sm.initialize_all())
        self.assertEqual(self.sm._states["TestService"], LifecycleState.INITIALIZED)

        self.sm.start_all()
        self.assertEqual(self.sm._states["TestService"], LifecycleState.RUNNING)

        self.sm.stop_all()
        self.assertEqual(self.sm._states["TestService"], LifecycleState.STOPPED)

    def test_restart_backoff_policy(self):
        class BrokenService(MockService):
            def restart(self) -> bool:
                raise Exception("Persistent failure")

        svc = BrokenService("FailingService")
        svc._healthy = False
        self.sm.register_service("FailingService", svc)

        supervisor = ThreadSupervisor(self.sm, max_restarts=2)

        # Manually trigger failure recovery check twice
        supervisor._recover_service("FailingService")
        self.assertEqual(self.sm._metrics["FailingService"]["restart_count"], 1)
        self.assertEqual(
            self.sm._backoff_delays["FailingService"], 2.0
        )  # Check delay incremented

        supervisor._recover_service("FailingService")
        self.assertEqual(self.sm._metrics["FailingService"]["restart_count"], 2)
        self.assertEqual(
            self.sm._backoff_delays["FailingService"], 5.0
        )  # Check delay incremented again

        # Third recovery attempt should trigger critical failure state
        supervisor._recover_service("FailingService")
        self.assertEqual(self.sm._states["FailingService"], LifecycleState.FAILED)


if __name__ == "__main__":
    unittest.main()
