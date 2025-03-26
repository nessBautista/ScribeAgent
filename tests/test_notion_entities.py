from datetime import datetime
from scribeagent.domain.notion.value_objects import NotionObject, RichTextContent, Parent
from scribeagent.domain.notion.enums import NotionObjectType, BlockType
from scribeagent.domain.notion.value_objects import TitlePropertyValue, RichTextPropertyValue, CheckboxPropertyValue, PropertyType, PropertyValue, GenericPropertyValue
from scribeagent.domain.notion.entities import (
    Block,
    TextBlock,
    ParagraphBlock,
    HeadingBlock,
    BulletedListItemBlock,
    NumberedListItemBlock,
    ToDoBlock,
    Page,
    Database,
    CodeBlock
)
import pytest


def test_rich_text_content_from_api():
    # Test data that mimics Notion API response
    api_data = [{
        "type": "text",
        "text": {
            "content": "Hello world",
            "link": None
        },
        "annotations": {
            "bold": False,
            "italic": True,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default"
        },
        "plain_text": "Hello world",
        "href": None
    }]

    # Convert API data to RichTextContent objects
    rich_text_list = RichTextContent.from_api(api_data)

    assert len(rich_text_list) == 1
    rich_text = rich_text_list[0]
    assert rich_text.content == "Hello world"
    assert rich_text.plain_text == "Hello world"
    assert rich_text.annotations["italic"] is True
    assert rich_text.href is None


def test_parent_from_api():
    # Test page parent
    page_parent_data = {
        "type": "page_id",
        "page_id": "123456"
    }
    page_parent = Parent.from_api(page_parent_data)
    assert page_parent.type == "page_id"
    assert page_parent.id == "123456"

    # Test database parent
    db_parent_data = {
        "type": "database_id",
        "database_id": "789012"
    }
    db_parent = Parent.from_api(db_parent_data)
    assert db_parent.type == "database_id"
    assert db_parent.id == "789012"

    # Test workspace parent
    workspace_parent_data = {
        "type": "workspace",
    }
    workspace_parent = Parent.from_api(workspace_parent_data)
    assert workspace_parent.type == "workspace"
    assert workspace_parent.id is None


# Example concrete implementation for testing NotionObject
class ExampleNotionObject(NotionObject):
    @classmethod
    def from_api(cls, data):
        return cls(
            id=data["id"],
            object_type=NotionObjectType(data["object"])
        )


def test_notion_object():
    # Test data
    api_data = {
        "object": "page",
        "id": "page_id_123"
    }
    
    # Create object
    obj = ExampleNotionObject.from_api(api_data)
    
    assert obj.id == "page_id_123"
    assert obj.object_type == NotionObjectType.PAGE


def test_title_property_value_from_api():
    # Test data mimicking Notion API response for a title property
    api_data = {
        "type": "title",
        "title": [{
            "type": "text",
            "text": {
                "content": "My Title",
                "link": None
            },
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            },
            "plain_text": "My Title",
            "href": None
        }]
    }
    
    title_prop = TitlePropertyValue.from_api("prop_id", api_data)
    
    assert title_prop.id == "prop_id"
    assert title_prop.type == PropertyType.TITLE
    assert len(title_prop.title) == 1
    assert title_prop.title[0].content == "My Title"
    assert title_prop.get_plain_text() == "My Title"


def test_rich_text_property_value_from_api():
    # Test data mimicking Notion API response for a rich text property
    api_data = {
        "type": "rich_text",
        "rich_text": [{
            "type": "text",
            "text": {
                "content": "Rich text content",
                "link": None
            },
            "annotations": {
                "bold": True,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default"
            },
            "plain_text": "Rich text content",
            "href": None
        }]
    }
    
    rich_text_prop = RichTextPropertyValue.from_api("prop_id", api_data)
    
    assert rich_text_prop.id == "prop_id"
    assert rich_text_prop.type == PropertyType.RICH_TEXT
    assert len(rich_text_prop.rich_text) == 1
    assert rich_text_prop.rich_text[0].content == "Rich text content"
    assert rich_text_prop.rich_text[0].annotations["bold"] is True
    assert rich_text_prop.get_plain_text() == "Rich text content"


def test_checkbox_property_value_from_api():
    # Test data mimicking Notion API response for a checkbox property
    api_data = {
        "type": "checkbox",
        "checkbox": True
    }
    
    checkbox_prop = CheckboxPropertyValue.from_api("prop_id", api_data)
    
    assert checkbox_prop.id == "prop_id"
    assert checkbox_prop.type == PropertyType.CHECKBOX
    assert checkbox_prop.checkbox is True

    # Test with false value
    api_data["checkbox"] = False
    checkbox_prop = CheckboxPropertyValue.from_api("prop_id", api_data)
    assert checkbox_prop.checkbox is False


def test_property_value_factory():
    # Test that PropertyValue.from_api creates the correct subclass
    title_data = {
        "type": "title",
        "title": [{
            "type": "text",
            "text": {"content": "Test Title"},
            "plain_text": "Test Title"
        }]
    }
    
    rich_text_data = {
        "type": "rich_text",
        "rich_text": [{
            "type": "text",
            "text": {"content": "Test Text"},
            "plain_text": "Test Text"
        }]
    }
    
    checkbox_data = {
        "type": "checkbox",
        "checkbox": True
    }
    
    # Test creation of different property types
    title_prop = PropertyValue.from_api("prop1", title_data)
    rich_text_prop = PropertyValue.from_api("prop2", rich_text_data)
    checkbox_prop = PropertyValue.from_api("prop3", checkbox_data)
    
    assert isinstance(title_prop, TitlePropertyValue)
    assert isinstance(rich_text_prop, RichTextPropertyValue)
    assert isinstance(checkbox_prop, CheckboxPropertyValue)
    
    # Test unsupported property type
    unsupported_data = {
        "type": "unsupported_type"
    }
    unsupported_prop = PropertyValue.from_api("prop4", unsupported_data)
    assert isinstance(unsupported_prop, GenericPropertyValue)
    assert unsupported_prop.get_plain_text() == "<Unsupported property type: unsupported_type>"


def test_block_factory():
    # Test data for different block types
    paragraph_data = {
        "object": "block",
        "id": "block_id",
        "type": "paragraph",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "has_children": False,
        "archived": False,
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "Test paragraph"},
                "plain_text": "Test paragraph"
            }],
            "color": "blue"
        }
    }
    
    heading_data = {
        "object": "block",
        "id": "block_id",
        "type": "heading_1",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "has_children": False,
        "archived": False,
        "heading_1": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "Test heading"},
                "plain_text": "Test heading"
            }],
            "color": "default",
            "is_toggleable": True
        }
    }
    
    todo_data = {
        "object": "block",
        "id": "block_id",
        "type": "to_do",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "has_children": False,
        "archived": False,
        "to_do": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "Test todo"},
                "plain_text": "Test todo"
            }],
            "checked": True,
            "color": "default"
        }
    }
    
    # Test block creation through factory method
    paragraph_block = Block.from_api(paragraph_data)
    heading_block = Block.from_api(heading_data)
    todo_block = Block.from_api(todo_data)
    
    # Test correct instance types
    assert isinstance(paragraph_block, ParagraphBlock)
    assert isinstance(heading_block, HeadingBlock)
    assert isinstance(todo_block, ToDoBlock)
    
    # Test common block properties
    assert paragraph_block.id == "block_id"
    assert paragraph_block.object_type == NotionObjectType.BLOCK
    assert not paragraph_block.has_children
    assert not paragraph_block.archived
    
    # Test specific block properties
    assert paragraph_block.color == "blue"
    assert paragraph_block.get_plain_text() == "Test paragraph"
    
    assert heading_block.level == 1
    assert heading_block.is_toggleable
    assert heading_block.get_plain_text() == "Test heading"
    
    assert todo_block.checked
    assert todo_block.get_plain_text() == "Test todo"


def test_text_block_plain_text():
    # Test getting plain text from blocks with multiple rich text segments
    data = {
        "object": "block",
        "id": "block_id",
        "type": "paragraph",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "has_children": False,
        "archived": False,
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "First "},
                    "plain_text": "First "
                },
                {
                    "type": "text",
                    "text": {"content": "second"},
                    "plain_text": "second"
                }
            ],
            "color": "default"
        }
    }
    
    block = ParagraphBlock.from_api(data)
    assert block.get_plain_text() == "First second"


def test_block_datetime_conversion():
    # Test proper conversion of ISO datetime strings
    data = {
        "object": "block",
        "id": "block_id",
        "type": "paragraph",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "has_children": False,
        "archived": False,
        "paragraph": {
            "rich_text": [],
            "color": "default"
        }
    }
    
    block = ParagraphBlock.from_api(data)
    
    assert block.created_time.year == 2024
    assert block.created_time.month == 3
    assert block.created_time.day == 23
    assert block.created_time.hour == 12
    assert block.created_time.minute == 0
    
    assert block.last_edited_time.hour == 12
    assert block.last_edited_time.minute == 30


def test_unsupported_block_type():
    # Test handling of unsupported block types
    data = {
        "object": "block",
        "id": "block_id",
        "type": "unsupported_type",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "has_children": False,
        "archived": False
    }
    
    # Now we expect the method to return a Block with UNSUPPORTED type
    block = Block.from_api(data)
    assert block.block_type == BlockType.UNSUPPORTED
    assert block.id == "block_id"
    assert block.has_children is False


def test_page_from_api():
    # Test data mimicking Notion API response for a page
    api_data = {
        "object": "page",
        "id": "page_id",
        "parent": {
            "type": "database_id",
            "database_id": "db_id"
        },
        "properties": {
            "Name": {
                "id": "title",
                "type": "title",
                "title": [{
                    "type": "text",
                    "text": {"content": "Test Page"},
                    "plain_text": "Test Page"
                }]
            },
            "Description": {
                "id": "desc",
                "type": "rich_text",
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "Test Description"},
                    "plain_text": "Test Description"
                }]
            }
        },
        "url": "https://notion.so/test-page",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "archived": False
    }
    
    page = Page.from_api(api_data)
    
    # Test basic properties
    assert page.id == "page_id"
    assert page.object_type == NotionObjectType.PAGE
    assert page.url == "https://notion.so/test-page"
    assert not page.archived
    
    # Test parent
    assert page.parent.type == "database_id"
    assert page.parent.id == "db_id"
    
    # Test properties
    assert len(page.properties) == 2
    assert isinstance(page.properties["Name"], TitlePropertyValue)
    assert isinstance(page.properties["Description"], RichTextPropertyValue)
    
    # Test title getter
    assert page.get_title() == "Test Page"


def test_database_from_api():
    # Test data mimicking Notion API response for a database
    api_data = {
        "object": "database",
        "id": "db_id",
        "parent": {
            "type": "page_id",
            "page_id": "parent_page_id"
        },
        "title": [{
            "type": "text",
            "text": {"content": "Test Database"},
            "plain_text": "Test Database"
        }],
        "properties": {
            "Name": {"type": "title", "title": {}},
            "Description": {"type": "rich_text", "rich_text": {}}
        },
        "url": "https://notion.so/test-database",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "archived": False
    }
    
    database = Database.from_api(api_data)
    
    # Test basic properties
    assert database.id == "db_id"
    assert database.object_type == NotionObjectType.DATABASE
    assert database.url == "https://notion.so/test-database"
    assert not database.archived
    
    # Test parent
    assert database.parent.type == "page_id"
    assert database.parent.id == "parent_page_id"
    
    # Test title
    assert len(database.title) == 1
    assert database.get_title() == "Test Database"
    
    # Test properties schema
    assert len(database.properties) == 2
    assert database.properties["Name"]["type"] == "title"
    assert database.properties["Description"]["type"] == "rich_text"


def test_page_without_title():
    """Test page behavior when no title property exists."""
    api_data = {
        "object": "page",
        "id": "page_id",
        "parent": {
            "type": "page_id",
            "page_id": "parent_id"
        },
        "properties": {
            "Description": {
                "id": "desc",
                "type": "rich_text",
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "Only description"},
                    "plain_text": "Only description"
                }]
            }
        },
        "url": "https://notion.so/test-page",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "archived": False
    }
    
    page = Page.from_api(api_data)
    assert page.get_title() == ""  # Should return empty string when no title exists


def test_page_with_empty_properties():
    """Test page creation with no properties."""
    api_data = {
        "object": "page",
        "id": "page_id",
        "parent": {
            "type": "workspace",
        },
        "properties": {},
        "url": "https://notion.so/test-page",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "archived": False
    }
    
    page = Page.from_api(api_data)
    assert len(page.properties) == 0
    assert page.get_title() == ""


def test_page_datetime_conversion():
    """Test datetime conversion in page objects."""
    api_data = {
        "object": "page",
        "id": "page_id",
        "parent": {"type": "workspace"},
        "properties": {},
        "url": "",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "archived": False
    }
    
    page = Page.from_api(api_data)
    
    assert page.created_time.year == 2024
    assert page.created_time.month == 3
    assert page.created_time.day == 23
    assert page.created_time.hour == 12
    assert page.created_time.minute == 0
    
    assert page.last_edited_time.hour == 12
    assert page.last_edited_time.minute == 30


def test_database_with_empty_title():
    """Test database with empty title."""
    api_data = {
        "object": "database",
        "id": "db_id",
        "parent": {
            "type": "page_id",
            "page_id": "parent_page_id"
        },
        "title": [],  # Empty title
        "properties": {
            "Name": {"type": "title", "title": {}}
        },
        "url": "https://notion.so/test-database",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "archived": False
    }
    
    database = Database.from_api(api_data)
    assert database.get_title() == ""  # Should return empty string for empty title


def test_database_with_multiple_title_segments():
    """Test database with multi-segment title."""
    api_data = {
        "object": "database",
        "id": "db_id",
        "parent": {
            "type": "page_id",
            "page_id": "parent_page_id"
        },
        "title": [
            {
                "type": "text",
                "text": {"content": "First "},
                "plain_text": "First "
            },
            {
                "type": "text",
                "text": {"content": "Second"},
                "plain_text": "Second"
            }
        ],
        "properties": {},
        "url": "https://notion.so/test-database",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "archived": False
    }
    
    database = Database.from_api(api_data)
    assert database.get_title() == "First Second"


def test_database_datetime_conversion():
    """Test datetime conversion in database objects."""
    api_data = {
        "object": "database",
        "id": "db_id",
        "parent": {"type": "workspace"},
        "title": [],
        "properties": {},
        "url": "",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "archived": False
    }
    
    database = Database.from_api(api_data)
    
    assert database.created_time.year == 2024
    assert database.created_time.month == 3
    assert database.created_time.day == 23
    assert database.created_time.hour == 12
    assert database.created_time.minute == 0
    
    assert database.last_edited_time.hour == 12
    assert database.last_edited_time.minute == 30 


def test_code_block_from_api():
    """Test creating a code block from API data."""
    # Test data
    code_data = {
        "object": "block",
        "id": "block_id",
        "type": "code",
        "created_time": "2024-03-23T12:00:00.000Z",
        "last_edited_time": "2024-03-23T12:30:00.000Z",
        "has_children": False,
        "archived": False,
        "code": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "func test() {\n    print(\"Hello world\")\n}"},
                "plain_text": "func test() {\n    print(\"Hello world\")\n}"
            }],
            "language": "swift",
            "caption": [{
                "type": "text",
                "text": {"content": "Example Swift function"},
                "plain_text": "Example Swift function"
            }]
        }
    }
    
    # Create block through factory method
    block = Block.from_api(code_data)
    
    # Test correct instance type
    assert isinstance(block, CodeBlock)
    
    # Test properties
    assert block.id == "block_id"
    assert block.block_type == BlockType.CODE
    assert block.language == "swift"
    assert block.get_plain_text() == "func test() {\n    print(\"Hello world\")\n}"
    assert len(block.caption) == 1
    assert block.caption[0].plain_text == "Example Swift function"