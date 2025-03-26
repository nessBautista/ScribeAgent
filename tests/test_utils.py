import pytest
from scribeagent.utils.NotionAPIUrlParser import NotionAPIUrlParser


class TestNotionAPIUrlParser:
    """Tests for NotionAPIUrlParser utility."""
    
    def test_extract_id_from_url_with_title(self):
        """Test extracting IDs from URLs with titles."""
        test_cases = [
            ("https://www.notion.so/my-page-123456789", "123456789"),
            ("https://www.notion.so/my-database-987654321", "987654321"),
            ("https://www.notion.so/my-complex-page-title-abcdef123", "abcdef123"),
            ("https://www.notion.so/workspace-test-page-name-xyz789", "xyz789"),
        ]
        
        for url, expected_id in test_cases:
            assert NotionAPIUrlParser.extract_id_from_url(url) == expected_id
    
    def test_extract_id_from_url_without_title(self):
        """Test extracting IDs from URLs without titles."""
        test_cases = [
            ("https://www.notion.so/123456789", "123456789"),
            ("https://notion.so/987654321", "987654321"),
            ("https://www.notion.so/abcdef123/", "abcdef123"),
        ]
        
        for url, expected_id in test_cases:
            assert NotionAPIUrlParser.extract_id_from_url(url) == expected_id
    
    def test_invalid_notion_urls(self):
        """Test handling of invalid Notion URLs."""
        # Test non-Notion domain
        with pytest.raises(ValueError, match="Not a valid Notion URL"):
            NotionAPIUrlParser.extract_id_from_url("https://example.com/page")
        
        # Test malformed URL
        with pytest.raises(ValueError, match="Not a valid Notion URL"):
            NotionAPIUrlParser.extract_id_from_url("not-a-url")
        
        # Test wrong domain
        with pytest.raises(ValueError, match="Not a valid Notion URL"):
            NotionAPIUrlParser.extract_id_from_url("http://notnotion.so/page-123")
        
        # Test wrong TLD
        with pytest.raises(ValueError, match="Not a valid Notion URL"):
            NotionAPIUrlParser.extract_id_from_url("https://notion.com/page-123")
    
    def test_empty_or_invalid_paths(self):
        """Test handling of empty or invalid paths."""
        invalid_paths = [
            "https://notion.so/",  # Empty path
            "https://notion.so//",  # Double slash
            "https://www.notion.so",  # No path
        ]
        
        for url in invalid_paths:
            with pytest.raises(ValueError, match="Could not extract ID from URL"):
                NotionAPIUrlParser.extract_id_from_url(url)
    
    def test_url_variations(self):
        """Test handling of URL variations."""
        test_cases = [
            # With/without www
            ("https://www.notion.so/page-123", "123"),
            ("https://notion.so/page-123", "123"),
            # With/without trailing slash
            ("https://notion.so/page-123/", "123"),
            ("https://www.notion.so/page-123/", "123"),
            # With query parameters
            ("https://www.notion.so/page-123?pvs=4", "123"),
            ("https://notion.so/test-456?p=1&v=2", "456"),
        ]
        
        for url, expected_id in test_cases:
            assert NotionAPIUrlParser.extract_id_from_url(url) == expected_id


