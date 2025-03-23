from datetime import datetime
from scribeagent.domain.notion.value_objects import NotionObject, RichTextContent, Parent
from scribeagent.domain.notion.enums import NotionObjectType
from scribeagent.domain.notion.value_objects import TitlePropertyValue, RichTextPropertyValue, CheckboxPropertyValue, PropertyType, PropertyValue
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
    with pytest.raises(NotImplementedError):
        PropertyValue.from_api("prop4", unsupported_data) 