import pytest
from unittest.mock import Mock, patch

from scribeagent.application.services.notion_services import NotionPageService
from scribeagent.domain.notion.entities import Page, Block, ParagraphBlock, CodeBlock
from scribeagent.domain.notion.repositories import PageRepository
from scribeagent.utils.NotionAPIUrlParser import NotionAPIUrlParser
from scribeagent.domain.notion.enums import NotionObjectType, BlockType
from datetime import datetime


class TestNotionPageService:
    """Tests for the NotionPageService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.page_repository = Mock(spec=PageRepository)
        self.url_parser = Mock(spec=NotionAPIUrlParser)
        self.service = NotionPageService(self.page_repository, self.url_parser)
        
        # Create a sample page and blocks for testing
        self.sample_page = self._create_sample_page()
        self.sample_blocks = self._create_sample_blocks()
        
        # Configure mocks
        self.page_repository.get_page.return_value = self.sample_page
        self.page_repository.get_page_content.return_value = self.sample_blocks
        self.url_parser.extract_id_from_url.return_value = "test_page_id"
    
    def _create_sample_page(self):
        """Create a sample page for testing."""
        return Mock(spec=Page, id="test_page_id", object_type=NotionObjectType.PAGE)
    
    def _create_sample_blocks(self):
        """Create sample blocks for testing."""
        return [
            Mock(spec=ParagraphBlock, id="block1", block_type=BlockType.PARAGRAPH),
            Mock(spec=ParagraphBlock, id="block2", block_type=BlockType.PARAGRAPH)
        ]
    
    def test_get_page_by_url(self):
        """Test getting a page by URL."""
        # Call the method
        page = self.service.get_page_by_url("https://www.notion.so/test-page-123")
        
        # Verify the URL was parsed
        self.url_parser.extract_id_from_url.assert_called_once_with("https://www.notion.so/test-page-123")
        
        # Verify the repository was called with the correct ID
        self.page_repository.get_page.assert_called_once_with("test_page_id")
        
        # Verify the result
        assert page == self.sample_page
    
    def test_get_page_content_by_url(self):
        """Test getting page content by URL."""
        # Call the method
        blocks = self.service.get_page_content_by_url("https://www.notion.so/test-page-123")
        
        # Verify the URL was parsed
        self.url_parser.extract_id_from_url.assert_called_once_with("https://www.notion.so/test-page-123")
        
        # Verify the repository was called with the correct ID
        self.page_repository.get_page_content.assert_called_once_with("test_page_id")
        
        # Verify the result
        assert blocks == self.sample_blocks
    
    def test_get_page_with_content_using_url(self):
        """Test getting a page with content using a URL."""
        # Call the method
        page, blocks = self.service.get_page_with_content("https://www.notion.so/test-page-123")
        
        # Verify the URL was parsed
        self.url_parser.extract_id_from_url.assert_called_once_with("https://www.notion.so/test-page-123")
        
        # Verify the repository was called with the correct ID
        self.page_repository.get_page.assert_called_once_with("test_page_id")
        self.page_repository.get_page_content.assert_called_once_with("test_page_id")
        
        # Verify the results
        assert page == self.sample_page
        assert blocks == self.sample_blocks
    
    def test_get_page_with_content_using_id(self):
        """Test getting a page with content using an ID directly."""
        # Call the method
        page, blocks = self.service.get_page_with_content("direct_page_id")
        
        # Verify the URL parser was not called
        self.url_parser.extract_id_from_url.assert_not_called()
        
        # Verify the repository was called with the correct ID
        self.page_repository.get_page.assert_called_once_with("direct_page_id")
        self.page_repository.get_page_content.assert_called_once_with("direct_page_id")
        
        # Verify the results
        assert page == self.sample_page
        assert blocks == self.sample_blocks
    
    def test_integration_with_real_dependencies(self):
        """Test with real dependencies (but mocked repositories)."""
        # Create a real URL parser and mock repository
        real_url_parser = NotionAPIUrlParser()
        mock_repository = Mock(spec=PageRepository)
        mock_repository.get_page.return_value = self.sample_page
        mock_repository.get_page_content.return_value = self.sample_blocks
        
        # Create service with real parser
        service = NotionPageService(mock_repository, real_url_parser)
        
        # Test with a real Notion URL
        test_url = "https://www.notion.so/Test-Page-abc123def456"
        page, blocks = service.get_page_with_content(test_url)
        
        # Verify the repository was called with the correct extracted ID
        mock_repository.get_page.assert_called_once_with("abc123def456")
        mock_repository.get_page_content.assert_called_once_with("abc123def456")
        
        # Verify the results
        assert page == self.sample_page
        assert blocks == self.sample_blocks 
    
    def test_search_blocks_with_nested_content(self):
        """Test searching blocks with nested content."""
        # Create a parent block with nested content
        parent_block = Mock(spec=ParagraphBlock)
        parent_block.block_type = BlockType.PARAGRAPH
        parent_block.get_plain_text.return_value = "Parent content"
        parent_block.has_children = True
        
        # Create a child block that matches the search
        child_block = Mock(spec=ParagraphBlock)
        child_block.block_type = BlockType.PARAGRAPH
        child_block.get_plain_text.return_value = "Matching child content"
        child_block.has_children = False
        child_block.children = []
        
        # Set up parent-child relationship
        parent_block.children = [child_block]
        
        # Update sample blocks
        self.sample_blocks = [parent_block]
        self.page_repository.get_page_content.return_value = self.sample_blocks
        
        # Search for content in child block
        matching_blocks = self.service.search_blocks("matching", "https://www.notion.so/test-page-123")
        
        # Verify URL parsing and repository calls
        self.url_parser.extract_id_from_url.assert_called_once_with("https://www.notion.so/test-page-123")
        self.page_repository.get_page_content.assert_called_once_with("test_page_id")
        
        # Verify search results
        assert len(matching_blocks) == 1
        assert matching_blocks[0]["type"] == "paragraph"
        assert matching_blocks[0]["content"] == "Matching child content"
    
    def test_search_blocks_with_code_block(self):
        """Test searching blocks with code content."""
        # Create a code block
        code_block = Mock(spec=CodeBlock)
        code_block.block_type = BlockType.CODE
        code_block.get_plain_text.return_value = "def search_test():\n    return 'found'"
        code_block.language = "python"
        code_block.has_children = False
        code_block.children = []
        
        # Update sample blocks
        self.sample_blocks = [code_block]
        self.page_repository.get_page_content.return_value = self.sample_blocks
        
        # Search for content in code block
        matching_blocks = self.service.search_blocks("search_test", "https://www.notion.so/test-page-123")
        
        # Verify search results
        assert len(matching_blocks) == 1
        assert matching_blocks[0]["type"] == "code"
        assert matching_blocks[0]["content"] == "def search_test():\n    return 'found'"
        assert matching_blocks[0]["language"] == "python"
    
    def test_search_blocks_with_deep_nesting(self):
        """Test searching blocks with multiple levels of nesting."""
        # Create a deeply nested structure
        top_block = Mock(spec=ParagraphBlock)
        top_block.block_type = BlockType.PARAGRAPH
        top_block.get_plain_text.return_value = "Top level"
        top_block.has_children = True
        
        mid_block = Mock(spec=ParagraphBlock)
        mid_block.block_type = BlockType.PARAGRAPH
        mid_block.get_plain_text.return_value = "Middle level"
        mid_block.has_children = True
        
        bottom_block = Mock(spec=CodeBlock)
        bottom_block.block_type = BlockType.CODE
        bottom_block.get_plain_text.return_value = "def nested_function():\n    print('found')"
        bottom_block.language = "python"
        bottom_block.has_children = False
        bottom_block.children = []
        
        # Set up the nesting
        mid_block.children = [bottom_block]
        top_block.children = [mid_block]
        
        # Update sample blocks
        self.sample_blocks = [top_block]
        self.page_repository.get_page_content.return_value = self.sample_blocks
        
        # Search for content in the deepest block
        matching_blocks = self.service.search_blocks("nested_function", "https://www.notion.so/test-page-123")
        
        # Verify search results
        assert len(matching_blocks) == 1
        assert matching_blocks[0]["type"] == "code"
        assert matching_blocks[0]["content"] == "def nested_function():\n    print('found')"
        assert matching_blocks[0]["language"] == "python"
        
        # Verify the block hierarchy is preserved
        assert "children" not in matching_blocks[0]  # Leaf node should not have children
    
    def test_search_blocks_no_matches(self):
        """Test searching blocks with no matches."""
        # Create a block with no matching content
        block = Mock(spec=ParagraphBlock)
        block.block_type = BlockType.PARAGRAPH
        block.get_plain_text.return_value = "No matching content here"
        block.has_children = False
        block.children = []
        
        # Update sample blocks
        self.sample_blocks = [block]
        self.page_repository.get_page_content.return_value = self.sample_blocks
        
        # Search for non-existent content
        matching_blocks = self.service.search_blocks("nonexistent", "https://www.notion.so/test-page-123")
        
        # Verify search results
        assert len(matching_blocks) == 0