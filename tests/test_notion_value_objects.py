import pytest
from unittest.mock import patch
from scribeagent.domain.notion.value_objects import (
    PropertyValue, GenericPropertyValue, TitlePropertyValue, 
    RichTextPropertyValue, CheckboxPropertyValue, PropertyType
)


class TestPropertyValue:
    def test_from_api_with_title_property(self):
        # Arrange
        property_id = "test_id"
        data = {
            "type": "title",
            "title": [{"type": "text", "text": {"content": "Test Title"}, "plain_text": "Test Title"}]
        }
        
        # Act
        result = PropertyValue.from_api(property_id, data)
        
        # Assert
        assert isinstance(result, TitlePropertyValue)
        assert result.id == property_id
        assert result.type == PropertyType.TITLE
        assert result.get_plain_text() == "Test Title"
    
    def test_from_api_with_rich_text_property(self):
        # Arrange
        property_id = "test_id"
        data = {
            "type": "rich_text",
            "rich_text": [{"type": "text", "text": {"content": "Test Text"}, "plain_text": "Test Text"}]
        }
        
        # Act
        result = PropertyValue.from_api(property_id, data)
        
        # Assert
        assert isinstance(result, RichTextPropertyValue)
        assert result.id == property_id
        assert result.type == PropertyType.RICH_TEXT
        assert result.get_plain_text() == "Test Text"
    
    def test_from_api_with_checkbox_property(self):
        # Arrange
        property_id = "test_id"
        data = {
            "type": "checkbox",
            "checkbox": True
        }
        
        # Act
        result = PropertyValue.from_api(property_id, data)
        
        # Assert
        assert isinstance(result, CheckboxPropertyValue)
        assert result.id == property_id
        assert result.type == PropertyType.CHECKBOX
        assert result.checkbox is True
    
    @patch('builtins.print')
    def test_from_api_with_unsupported_property_type(self, mock_print):
        # Arrange
        property_id = "test_id"
        data = {
            "type": "unique_id",
            "unique_id": {"prefix": "WOR", "number": 128}
        }
        
        # Act
        result = PropertyValue.from_api(property_id, data)
        
        # Assert
        assert isinstance(result, GenericPropertyValue)
        assert result.id == property_id
        assert result.type == PropertyType.TITLE  # Placeholder type
        assert result.data == data
        assert "unique_id" in result.get_plain_text()
        mock_print.assert_called_once()
    
    @patch('builtins.print')
    def test_from_api_with_unimplemented_property_type(self, mock_print):
        # Arrange
        property_id = "test_id"
        data = {
            "type": "multi_select",
            "multi_select": [{"id": "123", "name": "Option 1", "color": "blue"}]
        }
        
        # Act
        result = PropertyValue.from_api(property_id, data)
        
        # Assert
        assert isinstance(result, GenericPropertyValue)
        assert result.id == property_id
        assert result.type == PropertyType.TITLE  # Placeholder type
        assert result.data == data
        assert "multi_select" in result.get_plain_text()
        mock_print.assert_called_once()


class TestGenericPropertyValue:
    def test_from_api(self):
        # Arrange
        property_id = "test_id"
        data = {
            "type": "url",
            "url": "https://example.com"
        }
        
        # Act
        result = GenericPropertyValue.from_api(property_id, data)
        
        # Assert
        assert isinstance(result, GenericPropertyValue)
        assert result.id == property_id
        assert result.type == PropertyType.TITLE  # Placeholder type
        assert result.data == data
        assert result.get_plain_text() == "<Unsupported property type: url>" 