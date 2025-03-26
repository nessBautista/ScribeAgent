import pytest
from unittest.mock import patch, MagicMock
from scribeagent.infrastructure.notion.api_client import NotionAPIClient


class TestNotionAPIClient:
    def test_init(self):
        # Arrange & Act
        client = NotionAPIClient(api_key="test_key", debug=True)
        
        # Assert
        assert client.api_key == "test_key"
        assert client.debug is True
        assert client.base_url == "https://api.notion.com/v1"
        assert "Authorization" in client.headers
        assert "Notion-Version" in client.headers
        assert "Content-Type" in client.headers
    
    @patch('requests.request')
    @patch('builtins.print')
    def test_make_request_with_debug_enabled(self, mock_print, mock_request):
        # Arrange
        client = NotionAPIClient(api_key="test_key", debug=True)
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"id": "123"}]}
        mock_request.return_value = mock_response
        
        # Act
        result = client._make_request("GET", "/test_endpoint")
        
        # Assert
        mock_request.assert_called_once()
        assert mock_print.call_count >= 3  # At least 3 print calls for debug output
        assert result == {"results": [{"id": "123"}]}
    
    @patch('requests.request')
    def test_make_request_with_debug_disabled(self, mock_request):
        # Arrange
        client = NotionAPIClient(api_key="test_key", debug=False)
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"id": "123"}]}
        mock_request.return_value = mock_response
        
        # Act
        with patch('builtins.print') as mock_print:
            result = client._make_request("GET", "/test_endpoint")
        
        # Assert
        mock_request.assert_called_once()
        mock_print.assert_not_called()  # No debug output
        assert result == {"results": [{"id": "123"}]} 