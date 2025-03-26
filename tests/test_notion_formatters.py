import pytest
from rich.console import Console
from scribeagent.domain.notion.entities import Block, CodeBlock, TextBlock, ParagraphBlock
from scribeagent.domain.notion.enums import BlockType
from scribeagent.utils.notion_formatters import NotionBlockFormatter
from unittest.mock import Mock, patch
from unittest.mock import call


def test_format_as_dict_text_block():
    """Test formatting a text block as dictionary."""
    # Create a mock text block
    text_block = Mock(spec=TextBlock)
    text_block.block_type = BlockType.PARAGRAPH
    text_block.get_plain_text.return_value = "Test paragraph"
    text_block.has_children = False
    text_block.children = []
    
    # Format block
    result = NotionBlockFormatter.format_as_dict(text_block)
    
    assert result == {
        "type": "paragraph",
        "content": "Test paragraph"
    }


def test_format_as_dict_code_block():
    """Test formatting a code block as dictionary."""
    # Create a mock code block
    code_block = Mock(spec=CodeBlock)
    code_block.block_type = BlockType.CODE
    code_block.get_plain_text.return_value = "def test():\n    pass"
    code_block.language = "python"
    code_block.has_children = False
    code_block.children = []
    code_block.caption = []
    
    # Format block
    result = NotionBlockFormatter.format_as_dict(code_block)
    
    assert result == {
        "type": "code",
        "content": "def test():\n    pass",
        "language": "python"
    }


def test_format_as_dict_with_children():
    """Test formatting a block with children as dictionary."""
    # Create parent block
    parent_block = Mock(spec=ParagraphBlock)
    parent_block.block_type = BlockType.PARAGRAPH
    parent_block.get_plain_text.return_value = "Parent paragraph"
    parent_block.has_children = True
    
    # Create child block
    child_block = Mock(spec=CodeBlock)
    child_block.block_type = BlockType.CODE
    child_block.get_plain_text.return_value = "print('hello')"
    child_block.language = "python"
    child_block.has_children = False
    child_block.children = []
    child_block.caption = []
    
    parent_block.children = [child_block]
    
    # Format block
    result = NotionBlockFormatter.format_as_dict(parent_block)
    
    assert result == {
        "type": "paragraph",
        "content": "Parent paragraph",
        "children": [{
            "type": "code",
            "content": "print('hello')",
            "language": "python"
        }]
    }


@patch('rich.console.Console')
def test_format_as_rich_text_block(mock_console):
    """Test rich formatting of a text block."""
    # Create mock console
    console = Mock(spec=Console)
    
    # Create mock text block
    text_block = Mock(spec=TextBlock)
    text_block.block_type = BlockType.PARAGRAPH
    text_block.get_plain_text.return_value = "Test paragraph"
    text_block.has_children = False
    text_block.children = []
    
    # Format block
    NotionBlockFormatter.format_as_rich(text_block, indent_level=0, console=console)
    
    # Verify console output
    console.print.assert_called_once_with(
        "- [bold blue]paragraph[/bold blue]: Test paragraph"
    )


@patch('rich.console.Console')
def test_format_as_rich_code_block(mock_console):
    """Test rich formatting of a code block."""
    # Create mock console
    console = Mock(spec=Console)
    
    # Create mock code block
    code_block = Mock(spec=CodeBlock)
    code_block.block_type = BlockType.CODE
    code_block.get_plain_text.return_value = "def test():\n    pass"
    code_block.language = "python"
    code_block.has_children = False
    code_block.children = []
    code_block.caption = []
    
    # Format block
    NotionBlockFormatter.format_as_rich(code_block, indent_level=0, console=console)
    
    # Verify console output
    assert len(console.print.call_args_list) == 2
    first_call = console.print.call_args_list[0]
    second_call = console.print.call_args_list[1]
    
    assert first_call == call("- [bold blue]code[/bold blue] ([bold yellow]python[/bold yellow]):")
    # Second call should contain a Syntax object, but we don't care about its specific memory address
    assert "Syntax object at" in str(second_call)


@patch('rich.console.Console')
def test_format_as_rich_with_children(mock_console):
    """Test rich formatting of a block with children."""
    # Create mock console
    console = Mock(spec=Console)
    
    # Create parent block
    parent_block = Mock(spec=ParagraphBlock)
    parent_block.block_type = BlockType.PARAGRAPH
    parent_block.get_plain_text.return_value = "Parent paragraph"
    parent_block.has_children = True
    
    # Create child block
    child_block = Mock(spec=ParagraphBlock)
    child_block.block_type = BlockType.PARAGRAPH
    child_block.get_plain_text.return_value = "Child paragraph"
    child_block.has_children = False
    child_block.children = []
    
    parent_block.children = [child_block]
    
    # Format block
    NotionBlockFormatter.format_as_rich(parent_block, indent_level=0, console=console)
    
    # Verify console output
    expected_calls = [
        call("- [bold blue]paragraph[/bold blue]: Parent paragraph"),
        call("    - [bold blue]paragraph[/bold blue]: Child paragraph")
    ]
    assert console.print.call_args_list == expected_calls 