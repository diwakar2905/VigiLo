from abc import ABC, abstractmethod

class IService(ABC):
    """Base interface for all application services."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize service resources."""
        pass
        
    @abstractmethod
    def shutdown(self) -> None:
        """Clean up service resources."""
        pass
