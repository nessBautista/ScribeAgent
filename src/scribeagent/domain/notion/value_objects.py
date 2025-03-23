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


@dataclass
class PropertyValue(ABC):
    """Base class for property values."""
    id: str
    type: PropertyType
    
    @classmethod
    def from_api(cls, id: str, data: Dict[str, Any]) -> "PropertyValue":
        """Create a property value from API response data."""
        try:
            property_type = PropertyType(data.get("type"))
        except ValueError:
            raise NotImplementedError(f"Property type {data.get('type')} not implemented")
        
        if property_type == PropertyType.TITLE:
            return TitlePropertyValue.from_api(id, data)
        elif property_type == PropertyType.RICH_TEXT:
            return RichTextPropertyValue.from_api(id, data)
        elif property_type == PropertyType.CHECKBOX:
            return CheckboxPropertyValue.from_api(id, data)
        else:
            raise NotImplementedError(f"Property type {property_type} not implemented")


@dataclass
class TitlePropertyValue(PropertyValue):
    """Title property value."""
    title: List[RichTextContent] = field(default_factory=list)
    
    @classmethod
    def from_api(cls, id: str, data: Dict[str, Any]) -> "TitlePropertyValue":
        """Create a title property value from API response data."""
        title_data = data.get("title", [])
        return cls(
            id=id,
            type=PropertyType.TITLE,
            title=RichTextContent.from_api(title_data)
        )
    
    def get_plain_text(self) -> str:
        """Get the plain text of the title."""
        return ''.join(text.plain_text for text in self.title)


@dataclass
class RichTextPropertyValue(PropertyValue):
    """Rich text property value."""
    rich_text: List[RichTextContent] = field(default_factory=list)
    
    @classmethod
    def from_api(cls, id: str, data: Dict[str, Any]) -> "RichTextPropertyValue":
        """Create a rich text property value from API response data."""
        rich_text_data = data.get("rich_text", [])
        return cls(
            id=id,
            type=PropertyType.RICH_TEXT,
            rich_text=RichTextContent.from_api(rich_text_data)
        )
    
    def get_plain_text(self) -> str:
        """Get the plain text of the rich text."""
        return ''.join(text.plain_text for text in self.rich_text)


@dataclass
class CheckboxPropertyValue(PropertyValue):
    """Checkbox property value."""
    checkbox: bool = False
    
    @classmethod
    def from_api(cls, id: str, data: Dict[str, Any]) -> "CheckboxPropertyValue":
        """Create a checkbox property value from API response data."""
        return cls(
            id=id,
            type=PropertyType.CHECKBOX,
            checkbox=data.get("checkbox", False)
        )