from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
import requests
from urllib.parse import urlparse


class NotionObjectType(Enum):
    """Types of objects in Notion."""
    PAGE = "page"
    DATABASE = "database"
    BLOCK = "block"
    USER = "user"
    RICH_TEXT = "rich_text"
    PROPERTY_ITEM = "property_item"


class PropertyType(Enum):
    """Types of properties in Notion."""
    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    PEOPLE = "people"
    FILES = "files"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    FORMULA = "formula"
    RELATION = "relation"
    ROLLUP = "rollup"
    CREATED_TIME = "created_time"
    CREATED_BY = "created_by"
    LAST_EDITED_TIME = "last_edited_time"
    LAST_EDITED_BY = "last_edited_by"
    STATUS = "status"


class BlockType(Enum):
    """Types of blocks in Notion."""
    PARAGRAPH = "paragraph"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    BULLETED_LIST_ITEM = "bulleted_list_item"
    NUMBERED_LIST_ITEM = "numbered_list_item"
    TO_DO = "to_do"
    TOGGLE = "toggle"
    CHILD_PAGE = "child_page"
    CHILD_DATABASE = "child_database"
    CALLOUT = "callout"
    QUOTE = "quote"
    CODE = "code"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    DIVIDER = "divider"
    TABLE = "table"
    TABLE_ROW = "table_row"
    SYNCED_BLOCK = "synced_block"
    TEMPLATE = "template"
    LINK_TO_PAGE = "link_to_page"
    LINK_PREVIEW = "link_preview"
    BOOKMARK = "bookmark"
    EMBED = "embed"
    EQUATION = "equation"