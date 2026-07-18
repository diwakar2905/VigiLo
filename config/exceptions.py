# config/exceptions.py


class ConfigError(Exception):
    """Base exception for all configuration subsystem errors."""

    pass


class ValidationError(ConfigError):
    """Exception raised when configuration validation fails."""

    pass


class MigrationError(ConfigError):
    """Exception raised when configuration migration fails."""

    pass


class LoaderError(ConfigError):
    """Exception raised when configuration loading fails."""

    pass


class SaverError(ConfigError):
    """Exception raised when configuration saving fails."""

    pass
