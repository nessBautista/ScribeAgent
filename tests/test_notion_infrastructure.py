import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from datetime import datetime

from scribeagent.infrastructure.notion.api_client import NotionAPIClient
from scribeagent.infrastructure.notion.repositories import NotionAPIPageRepository, NotionAPIDatabaseRepository
from scribeagent.domain.notion.entities import Page, Block, Database, ParagraphBlock
from scribeagent.domain.notion.value_objects import Parent, RichTextContent
from scribeagent.domain.notion.enums import NotionObjectType, BlockType


class TestNotionAPIClient:
    """Tests for the Notion API client."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.client = NotionAPIClient(self.api_key)
    
    @patch('requests.request')
    def test_make_request(self, mock_request):
        """Test the _make_request method."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client._make_request("GET", "/test-endpoint", {"param": "value"}, {"data": "value"})
        
        # Assertions
        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.notion.com/v1/test-endpoint",
            headers={
                "Authorization": "Bearer test_api_key",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            },
            params={"param": "value"},
            json={"data": "value"}
        )
        assert result == {"success": True}
    
    @patch('requests.request')
    def test_get_page(self, mock_request):
        """Test the get_page method."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {"id": "page_id", "object": "page"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get_page("page_id")
        
        # Assertions
        mock_request.assert_called_once()
        assert mock_request.call_args[1]['url'] == "https://api.notion.com/v1/pages/page_id"
        assert result == {"id": "page_id", "object": "page"}
    
    @patch('requests.request')
    def test_get_block_children(self, mock_request):
        """Test the get_block_children method."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": "block_id", "object": "block"}],
            "has_more": False
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get_block_children("block_id")
        
        # Assertions
        mock_request.assert_called_once()
        assert mock_request.call_args[1]['url'] == "https://api.notion.com/v1/blocks/block_id/children"
        assert mock_request.call_args[1]['params'] == {"page_size": 100}
        assert result == {"results": [{"id": "block_id", "object": "block"}], "has_more": False}
    
    @patch('requests.request')
    def test_get_database(self, mock_request):
        """Test the get_database method."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {"id": "db_id", "object": "database"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.get_database("db_id")
        
        # Assertions
        mock_request.assert_called_once()
        assert mock_request.call_args[1]['url'] == "https://api.notion.com/v1/databases/db_id"
        assert result == {"id": "db_id", "object": "database"}
    
    @patch('requests.request')
    def test_query_database(self, mock_request):
        """Test the query_database method."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": "page_id", "object": "page"}],
            "has_more": False
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.client.query_database("db_id", {"filter": {"property": "Name", "equals": "Test"}})
        
        # Assertions
        mock_request.assert_called_once()
        assert mock_request.call_args[1]['url'] == "https://api.notion.com/v1/databases/db_id/query"
        assert mock_request.call_args[1]['json'] == {
            "page_size": 100,
            "filter": {"property": "Name", "equals": "Test"}
        }
        assert result == {"results": [{"id": "page_id", "object": "page"}], "has_more": False}
    
    @patch('requests.request')
    def test_error_handling(self, mock_request):
        """Test error handling in the API client."""
        # Setup mock response to raise an error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_request.return_value = mock_response
        
        # Call the method and check for exception
        with pytest.raises(requests.exceptions.HTTPError):
            self.client.get_page("page_id")


class TestNotionAPIPageRepository:
    """Tests for the Notion API page repository."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api_client = Mock()
        self.repository = NotionAPIPageRepository(self.api_client, max_depth=3)
    
    def test_get_page(self):
        """Test the get_page method."""
        # Setup mock response
        page_data = {
            "id": "page_id",
            "object": "page",
            "parent": {"type": "workspace"},
            "properties": {},
            "url": "https://notion.so/page_id",
            "created_time": "2023-01-01T00:00:00.000Z",
            "last_edited_time": "2023-01-02T00:00:00.000Z"
        }
        self.api_client.get_page.return_value = page_data
        
        # Call the method
        page = self.repository.get_page("page_id")
        
        # Assertions
        self.api_client.get_page.assert_called_once_with("page_id")
        assert isinstance(page, Page)
        assert page.id == "page_id"
        assert page.object_type == NotionObjectType.PAGE
    
    def test_get_page_content(self):
        """Test the get_page_content method."""
        # Setup mock responses
        block_data = {
            "results": [
                {
                    "id": "block_id",
                    "object": "block",
                    "type": "paragraph",
                    "created_time": "2023-01-01T00:00:00.000Z",
                    "last_edited_time": "2023-01-02T00:00:00.000Z",
                    "has_children": False,
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "Test"}, "plain_text": "Test"}]
                    }
                }
            ],
            "has_more": False
        }
        self.api_client.get_block_children.return_value = block_data
        
        # Call the method
        blocks = self.repository.get_page_content("page_id")
        
        # Assertions
        self.api_client.get_block_children.assert_called_once_with("page_id", None)
        assert len(blocks) == 1
        assert isinstance(blocks[0], Block)
        assert blocks[0].id == "block_id"
        assert blocks[0].block_type == BlockType.PARAGRAPH


class TestNotionAPIDatabaseRepository:
    """Tests for the Notion API database repository."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api_client = Mock()
        self.repository = NotionAPIDatabaseRepository(self.api_client)
    
    def test_get_database(self):
        """Test the get_database method."""
        # Setup mock response
        db_data = {
            "id": "db_id",
            "object": "database",
            "parent": {"type": "page_id", "page_id": "parent_id"},
            "title": [{"type": "text", "text": {"content": "Test DB"}, "plain_text": "Test DB"}],
            "properties": {},
            "url": "https://notion.so/db_id",
            "created_time": "2023-01-01T00:00:00.000Z",
            "last_edited_time": "2023-01-02T00:00:00.000Z"
        }
        self.api_client.get_database.return_value = db_data
        
        # Call the method
        database = self.repository.get_database("db_id")
        
        # Assertions
        self.api_client.get_database.assert_called_once_with("db_id")
        assert isinstance(database, Database)
        assert database.id == "db_id"
        assert database.object_type == NotionObjectType.DATABASE
        assert database.get_title() == "Test DB"
    
    def test_query_database(self):
        """Test the query_database method."""
        # Setup mock responses
        query_result = {
            "results": [
                {
                    "id": "page_id",
                    "object": "page",
                    "parent": {"type": "database_id", "database_id": "db_id"},
                    "properties": {},
                    "url": "https://notion.so/page_id",
                    "created_time": "2023-01-01T00:00:00.000Z",
                    "last_edited_time": "2023-01-02T00:00:00.000Z"
                }
            ],
            "has_more": False
        }
        self.api_client.query_database.return_value = query_result
        
        # Call the method
        pages = self.repository.query_database("db_id", {"filter": {"property": "Name", "equals": "Test"}})
        
        # Assertions
        self.api_client.query_database.assert_called_once_with(
            "db_id", 
            {"filter": {"property": "Name", "equals": "Test"}}, 
            None
        )
        assert len(pages) == 1
        assert isinstance(pages[0], Page)
        assert pages[0].id == "page_id"
        assert pages[0].object_type == NotionObjectType.PAGE
    
    def test_query_database_pagination(self):
        """Test database query pagination."""
        # Setup mock responses for two pages of results
        first_page = {
            "results": [{"id": "page1", "object": "page", "parent": {"type": "database_id", "database_id": "db_id"},
                        "properties": {}, "url": "", "created_time": "2023-01-01T00:00:00.000Z", 
                        "last_edited_time": "2023-01-02T00:00:00.000Z"}],
            "has_more": True,
            "next_cursor": "cursor123"
        }
        second_page = {
            "results": [{"id": "page2", "object": "page", "parent": {"type": "database_id", "database_id": "db_id"},
                        "properties": {}, "url": "", "created_time": "2023-01-01T00:00:00.000Z", 
                        "last_edited_time": "2023-01-02T00:00:00.000Z"}],
            "has_more": False
        }
        
        self.api_client.query_database.side_effect = [first_page, second_page]
        
        # Call the method
        pages = self.repository.query_database("db_id")
        
        # Assertions
        assert len(pages) == 2
        assert pages[0].id == "page1"
        assert pages[1].id == "page2"
        
        # Check that pagination was handled correctly
        assert self.api_client.query_database.call_count == 2
        self.api_client.query_database.assert_any_call("db_id", None, None)
        self.api_client.query_database.assert_any_call("db_id", None, "cursor123") 