from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from .entities import Page, Database, Block


class PageRepository(ABC):
    """Interface for page repository."""
    
    @abstractmethod
    def get_page(self, page_id: str) -> Page:
        """Get a page by ID."""
        pass
    
    @abstractmethod
    def get_page_content(self, page_id: str) -> List[Block]:
        """Get the content of a page."""
        pass


class DatabaseRepository(ABC):
    """Interface for database repository."""
    
    @abstractmethod
    def get_database(self, database_id: str) -> Database:
        """Get a database by ID."""
        pass
    
    @abstractmethod
    def query_database(self, database_id: str, filter_params: Optional[Dict[str, Any]] = None) -> List[Page]:
        """Query a database."""
        pass
