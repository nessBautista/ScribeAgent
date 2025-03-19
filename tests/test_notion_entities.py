from datetime import datetime
from scribeagent.domain.notion.value_objects import NotionObject, RichTextContent, Parent
from scribeagent.domain.notion.enums import NotionObjectType


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