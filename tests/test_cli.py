import pytest
from unittest.mock import patch, MagicMock
from scribeagent.cli import notion_get_page, main


class TestCLI:
    @patch('scribeagent.cli.create_notion_page_service')
    @patch('builtins.print')
    def test_notion_get_page(self, mock_print, mock_create_service):
        # Arrange
        mock_page = MagicMock()
        mock_page.get_title.return_value = "Test Page"
        mock_page.url = "https://notion.so/test"
        mock_page.created_time = "2023-01-01"
        mock_page.last_edited_time = "2023-01-02"
        
        mock_content = [MagicMock()]
        
        mock_service = MagicMock()
        mock_service.get_page_with_content.return_value = (mock_page, mock_content)
        mock_create_service.return_value = mock_service
        
        # Act
        with patch('os.getenv', return_value="test_api_key"):
            notion_get_page("https://notion.so/test", debug=True, max_depth=4)
        
        # Assert
        mock_create_service.assert_called_once_with("test_api_key", debug=True, max_depth=4)
        mock_service.get_page_with_content.assert_called_once_with("https://notion.so/test")
        assert mock_print.call_count >= 4  # At least 4 print calls for page info
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('scribeagent.cli.notion_get_page')
    def test_main_success(self, mock_notion_get_page, mock_parse_args):
        # Arrange
        mock_args = MagicMock()
        mock_args.url = "https://notion.so/test"
        mock_args.api_key = "test_key"
        mock_args.debug = True
        mock_args.max_depth = 3
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Act
        result = main()
        
        # Assert
        mock_notion_get_page.assert_called_once_with(
            "https://notion.so/test", "test_key", True, 3, False
        )
        assert result == 0
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('scribeagent.cli.notion_get_page')
    @patch('scribeagent.cli.Console')
    def test_main_error(self, mock_console_class, mock_notion_get_page, mock_parse_args):
        # Arrange
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        mock_args = MagicMock()
        mock_parse_args.return_value = mock_args
        mock_notion_get_page.side_effect = Exception("Test error")
        
        # Act
        result = main()
        
        # Assert
        mock_console.print.assert_called_once()
        assert result == 1

    @patch('requests.Session.request')
    @patch('scribeagent.cli.Console')
    def test_notion_get_page_verbose(self, mock_console_class, mock_request):
        # Arrange
        # Mock the HTTP request to prevent actual API calls
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "object": "page",
            "id": "test-id",
            "created_time": "2023-01-01T00:00:00.000Z",
            "last_edited_time": "2023-01-02T00:00:00.000Z",
            "url": "https://notion.so/test",
            "archived": False,
            "parent": {"type": "workspace", "workspace": True},
            "properties": {}
        }
        mock_request.return_value = mock_response
        
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        
        # Act
        with patch('os.getenv', return_value="test_api_key"):
            notion_get_page("https://notion.so/test", debug=True, max_depth=4, verbose=True)
        
        # Assert
        # Should have called console.print multiple times for verbose output
        assert mock_console.print.call_count > 0
        # Verify the HTTP request was made
        assert mock_request.call_count > 0