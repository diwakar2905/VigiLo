# PART IV — Coding Standards & Engineering

---

## Chapter 13 — Coding Standards

### 1. Style Guide Rules
All contributions must adhere to the following coding standards:
*   **PEP 8 Compliance**: Strictly checked via linting tools.
*   **Type Hinting**: All functions, method arguments, and return types must be fully annotated.
*   **Docstrings**: Modules and public interfaces must include Google-style docstrings.

---

## Chapter 14 — SOLID Guidelines in Python

### 1. Interface Segregation (ISP)
Each interface must define a single, focused responsibility. For example, `ISecretManager` handles cryptographic transformations, while `ISecretRotator` handles key rotation schedules.

### 2. Single Responsibility (SRP)
Each class has a single responsibility. `ConfigValidator` handles configuration validation checks, while `ConfigSaver` manages writing updates atomically to disk.

---

## Chapter 15 — Design Patterns Reference

### 1. Allowed Design Patterns
*   **Facade**: Used by the `SecurityCore` class to expose security components through a single orchestrator interface.
*   **Singleton**: Used by `ServiceManager` to allow global access to service registries and heartbeats.
*   **Strategy**: Used to define modular restart policies (`Always`, `OnFailure`, `Manual`, `Disabled`).

---

## Chapter 16 — Error Handling & Exceptions

### 1. Custom Exceptions Hierarchy
```
VigiLoException (Base)
 ├── ConfigError
 │    ├── ValidationError
 │    └── MigrationError
 └── SecurityError
      ├── AccessDeniedError
      └── PolicyViolationError
```

---

## Chapter 17 — Testing Strategy

### 1. Test Levels
*   **Unit Tests**: Validate logic in isolation (e.g. testing `ConfigValidator` with mocked inputs).
*   **Integration Tests**: Verify component interaction (e.g. checking dependency sorting in `ServiceManager`).

---

## Chapter 18 — CI/CD Pipeline

*   **Linter**: Code formatting is validated using Black and Ruff.
*   **Static Analysis**: Security analysis is run using CodeQL.

---

## Chapter 19 — Release Engineering

*   **Version Format**: Follows semantic versioning (`MAJOR.MINOR.PATCH`).
*   **Hotfixes**: Merged directly into `main` and tagged with patch increments.
