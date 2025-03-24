from .enums import NotionObjectType, PropertyType, BlockType
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
import requests
from urllib.parse import urlparse


@dataclass
class NotionObject(ABC):
    """Base class for all Notion objects."""
    id: str
    object_type: NotionObjectType
    
    @classmethod
    @abstractmethod
    def from_api(cls, data: Dict[str, Any]):
        """Create an object from API response data."""
        pass


@dataclass
class RichTextContent:
    """Represents rich text content in Notion."""
    content: str
    plain_text: str
    annotations: Optional[Dict[str, Any]] = None
    href: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: List[Dict[str, Any]]) -> List["RichTextContent"]:
        """Create rich text content from API response data."""
        result = []
        for item in data:
            if item["type"] == "text":
                text = item["text"]
                content = text.get("content", "")
                result.append(
                    cls(
                        content=content,
                        plain_text=item.get("plain_text", content),
                        annotations=item.get("annotations"),
                        href=item.get("href")
                    )
                )
        return result


@dataclass
class Parent:
    """Represents a parent of a Notion object."""
    type: str  # page_id, database_id, workspace, block_id
    id: Optional[str] = None
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Parent":
        """Create a parent from API response data."""
        parent_type = data.get("type")
        parent_id = None
        
        if parent_type == "page_id":
            parent_id = data.get("page_id")
        elif parent_type == "database_id":
            parent_id = data.get("database_id")
        elif parent_type == "block_id":
            parent_id = data.get("block_id")
            
        return cls(type=parent_type, id=parent_id)