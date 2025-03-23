from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any

from .value_objects import NotionObject, RichTextContent
from .enums import NotionObjectType, BlockType


@dataclass
class Block(NotionObject):
    """Base class for Notion blocks."""
    created_time: datetime
    last_edited_time: datetime
    has_children: bool
    block_type: BlockType
    archived: bool = False
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Block":
        """Create a block from API response data."""
        block_type = BlockType(data.get("type"))
        
        if block_type == BlockType.PARAGRAPH:
            return ParagraphBlock.from_api(data)
        elif block_type == BlockType.HEADING_1:
            return HeadingBlock.from_api(data, 1)
        elif block_type == BlockType.HEADING_2:
            return HeadingBlock.from_api(data, 2)
        elif block_type == BlockType.HEADING_3:
            return HeadingBlock.from_api(data, 3)
        elif block_type == BlockType.BULLETED_LIST_ITEM:
            return BulletedListItemBlock.from_api(data)
        elif block_type == BlockType.NUMBERED_LIST_ITEM:
            return NumberedListItemBlock.from_api(data)
        elif block_type == BlockType.TO_DO:
            return ToDoBlock.from_api(data)
        else:
            return cls(
                id=data.get("id"),
                object_type=NotionObjectType.BLOCK,
                created_time=datetime.fromisoformat(data.get("created_time").replace("Z", "+00:00")),
                last_edited_time=datetime.fromisoformat(data.get("last_edited_time").replace("Z", "+00:00")),
                has_children=data.get("has_children", False),
                block_type=block_type,
                archived=data.get("archived", False)
            )


@dataclass
class TextBlock(Block):
    """Base class for blocks containing rich text."""
    rich_text: List[RichTextContent] = field(default_factory=list)
    color: str = "default"
    
    def get_plain_text(self) -> str:
        """Get the plain text of the block."""
        return ''.join(text.plain_text for text in self.rich_text)


@dataclass
class ParagraphBlock(TextBlock):
    """Paragraph block."""
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "ParagraphBlock":
        """Create a paragraph block from API response data."""
        paragraph_data = data.get("paragraph", {})
        rich_text_data = paragraph_data.get("rich_text", [])
        
        return cls(
            id=data.get("id"),
            object_type=NotionObjectType.BLOCK,
            created_time=datetime.fromisoformat(data.get("created_time").replace("Z", "+00:00")),
            last_edited_time=datetime.fromisoformat(data.get("last_edited_time").replace("Z", "+00:00")),
            has_children=data.get("has_children", False),
            block_type=BlockType.PARAGRAPH,
            archived=data.get("archived", False),
            rich_text=RichTextContent.from_api(rich_text_data),
            color=paragraph_data.get("color", "default")
        )


@dataclass
class HeadingBlock(TextBlock):
    """Heading block."""
    level: int = 1
    is_toggleable: bool = False
    
    @classmethod
    def from_api(cls, data: Dict[str, Any], level: int) -> "HeadingBlock":
        """Create a heading block from API response data."""
        heading_key = f"heading_{level}"
        heading_data = data.get(heading_key, {})
        rich_text_data = heading_data.get("rich_text", [])
        
        return cls(
            id=data.get("id"),
            object_type=NotionObjectType.BLOCK,
            created_time=datetime.fromisoformat(data.get("created_time").replace("Z", "+00:00")),
            last_edited_time=datetime.fromisoformat(data.get("last_edited_time").replace("Z", "+00:00")),
            has_children=data.get("has_children", False),
            block_type=getattr(BlockType, f"HEADING_{level}"),
            archived=data.get("archived", False),
            rich_text=RichTextContent.from_api(rich_text_data),
            color=heading_data.get("color", "default"),
            level=level,
            is_toggleable=heading_data.get("is_toggleable", False)
        )


@dataclass
class BulletedListItemBlock(TextBlock):
    """Bulleted list item block."""
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "BulletedListItemBlock":
        """Create a bulleted list item block from API response data."""
        item_data = data.get("bulleted_list_item", {})
        rich_text_data = item_data.get("rich_text", [])
        
        return cls(
            id=data.get("id"),
            object_type=NotionObjectType.BLOCK,
            created_time=datetime.fromisoformat(data.get("created_time").replace("Z", "+00:00")),
            last_edited_time=datetime.fromisoformat(data.get("last_edited_time").replace("Z", "+00:00")),
            has_children=data.get("has_children", False),
            block_type=BlockType.BULLETED_LIST_ITEM,
            archived=data.get("archived", False),
            rich_text=RichTextContent.from_api(rich_text_data),
            color=item_data.get("color", "default")
        )


@dataclass
class NumberedListItemBlock(TextBlock):
    """Numbered list item block."""
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "NumberedListItemBlock":
        """Create a numbered list item block from API response data."""
        item_data = data.get("numbered_list_item", {})
        rich_text_data = item_data.get("rich_text", [])
        
        return cls(
            id=data.get("id"),
            object_type=NotionObjectType.BLOCK,
            created_time=datetime.fromisoformat(data.get("created_time").replace("Z", "+00:00")),
            last_edited_time=datetime.fromisoformat(data.get("last_edited_time").replace("Z", "+00:00")),
            has_children=data.get("has_children", False),
            block_type=BlockType.NUMBERED_LIST_ITEM,
            archived=data.get("archived", False),
            rich_text=RichTextContent.from_api(rich_text_data),
            color=item_data.get("color", "default")
        )


@dataclass
class ToDoBlock(TextBlock):
    """To-do block."""
    checked: bool = False
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "ToDoBlock":
        """Create a to-do block from API response data."""
        todo_data = data.get("to_do", {})
        rich_text_data = todo_data.get("rich_text", [])
        
        return cls(
            id=data.get("id"),
            object_type=NotionObjectType.BLOCK,
            created_time=datetime.fromisoformat(data.get("created_time").replace("Z", "+00:00")),
            last_edited_time=datetime.fromisoformat(data.get("last_edited_time").replace("Z", "+00:00")),
            has_children=data.get("has_children", False),
            block_type=BlockType.TO_DO,
            archived=data.get("archived", False),
            rich_text=RichTextContent.from_api(rich_text_data),
            color=todo_data.get("color", "default"),
            checked=todo_data.get("checked", False)
        )
