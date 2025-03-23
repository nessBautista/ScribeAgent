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
    CODE = "code"
    CHILD_PAGE = "child_page"
    CHILD_DATABASE = "child_database"
    EMBED = "embed"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    PDF = "pdf"
    BOOKMARK = "bookmark"
    CALLOUT = "callout"
    QUOTE = "quote"
    EQUATION = "equation"
    DIVIDER = "divider"
    TABLE_OF_CONTENTS = "table_of_contents"
    COLUMN = "column"
    COLUMN_LIST = "column_list"
    LINK_PREVIEW = "link_preview"
    SYNCED_BLOCK = "synced_block"
    TEMPLATE = "template"
    LINK_TO_PAGE = "link_to_page"
    TABLE = "table"
    TABLE_ROW = "table_row"
    UNSUPPORTED = "unsupported"