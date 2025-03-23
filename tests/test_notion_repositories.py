import pytest
from unittest.mock import patch, MagicMock
from scribeagent.infrastructure.notion.repositories import NotionAPIPageRepository
from scribeagent.domain.notion.entities import Block, Page


class TestNotionAPIPageRepository:
    def test_init(self):
        # Arrange
        api_client = MagicMock()
        
        # Act
        repo = NotionAPIPageRepository(api_client=api_client, max_depth=5)
        
        # Assert
        assert repo.api_client == api_client
        assert repo.max_depth == 5
    
    def test_get_page(self):
        # Arrange
        api_client = MagicMock()
        api_client.get_page.return_value = {"id": "page_id", "object": "page"}
        repo = NotionAPIPageRepository(api_client=api_client, max_depth=3)
        
        # Act
        with patch('scribeagent.domain.notion.entities.Page.from_api') as mock_from_api:
            mock_from_api.return_value = MagicMock(spec=Page)
            result = repo.get_page("page_id")
        
        # Assert
        api_client.get_page.assert_called_once_with("page_id")
        mock_from_api.assert_called_once()
        assert isinstance(result, Page)
    
    @patch('builtins.print')
    def test_get_page_content_max_depth_reached(self, mock_print):
        # Arrange
        api_client = MagicMock()
        repo = NotionAPIPageRepository(api_client=api_client, max_depth=2)
        
        # Act
        result = repo.get_page_content("block_id", current_depth=2)
        
        # Assert
        assert result == []
        mock_print.assert_called_once()
        assert "Maximum recursion depth" in mock_print.call_args[0][0]
    
    def test_get_page_content_with_children(self):
        # Arrange
        api_client = MagicMock()
        api_client.get_block_children.return_value = {
            "results": [
                {"id": "child1", "has_children": True},
                {"id": "child2", "has_children": False}
            ],
            "has_more": False
        }
        
        # Create the repository
        repo = NotionAPIPageRepository(api_client=api_client, max_depth=3)
        
        # Mock Block.from_api to return blocks with has_children property
        mock_block1 = MagicMock(spec=Block)
        mock_block1.id = "child1"
        mock_block1.has_children = True
        
        mock_block2 = MagicMock(spec=Block)
        mock_block2.id = "child2"
        mock_block2.has_children = False
        
        # Create a spy on the original method
        original_method = repo.get_page_content
        
        # Act
        with patch('scribeagent.domain.notion.entities.Block.from_api', side_effect=[mock_block1, mock_block2]):
            # Use a simpler approach - just track if the method was called with the right args
            with patch.object(repo, 'get_page_content', wraps=repo.get_page_content) as spy:
                # Override the method for recursive calls to avoid infinite recursion
                spy.side_effect = lambda id, current_depth: (
                    [] if id == "child1" and current_depth == 1 
                    else original_method(id, current_depth)
                )
                
                # Call the method
                result = repo.get_page_content("parent_id", current_depth=0)
        
        # Assert
        api_client.get_block_children.assert_called_once_with("parent_id", None)
        assert len(result) == 2
        assert result[0] == mock_block1
        assert result[1] == mock_block2
        # Verify the method was called with the right arguments
        spy.assert_any_call("child1", 1) 