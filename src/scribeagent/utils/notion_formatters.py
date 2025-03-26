from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.syntax import Syntax

from scribeagent.domain.notion.entities import Block, TextBlock, CodeBlock


class NotionBlockFormatter:
    """Utility for formatting Notion blocks in different output formats."""
    
    @staticmethod
    def format_as_dict(block, indent_level: int = 0) -> Dict[str, Any]:
        """Format a block as a dictionary for JSON serialization."""
        # Format the current block
        if isinstance(block, CodeBlock):
            block_info = {
                "type": block.block_type.value,
                "content": block.get_plain_text(),
                "language": block.language
            }
            if block.caption:
                block_info["caption"] = ''.join(caption.plain_text for caption in block.caption)
        elif isinstance(block, TextBlock):
            block_info = {
                "type": block.block_type.value,
                "content": block.get_plain_text()
            }
        else:
            block_info = {
                "type": block.block_type.value
            }
        
        # Add children if they exist
        if block.has_children and block.children:
            block_info["children"] = [NotionBlockFormatter.format_as_dict(child, indent_level + 1) 
                                     for child in block.children]
        
        return block_info
    
    @staticmethod
    def format_as_text(block, indent_level: int = 0) -> None:
        """Format a block as text and print to console."""
        indent = "    " * indent_level
        
        if isinstance(block, CodeBlock):
            print(f"{indent}- {block.block_type.value} ({block.language}):")
            print(f"{indent}```{block.language}")
            print(f"{indent}{block.get_plain_text()}")
            print(f"{indent}```")
            
            if block.caption:
                caption_text = ''.join(caption.plain_text for caption in block.caption)
                if caption_text:
                    print(f"{indent}Caption: {caption_text}")
        elif isinstance(block, TextBlock):
            print(f"{indent}- {block.block_type.value}: {block.get_plain_text()}")
        else:
            print(f"{indent}- {block.block_type.value}")
        
        # Process children if they exist
        if block.has_children and block.children:
            for child in block.children:
                NotionBlockFormatter.format_as_text(child, indent_level + 1)
    
    @staticmethod
    def format_as_rich(block, indent_level: int = 0, console: Optional[Console] = None) -> None:
        """Format a block with rich formatting and print to console."""
        if not console:
            console = Console()
            
        indent = "    " * indent_level
        
        if isinstance(block, CodeBlock):
            block_type = f"[bold blue]{block.block_type.value}[/bold blue]"
            language = f"[bold yellow]{block.language}[/bold yellow]"
            console.print(f"{indent}- {block_type} ({language}):")
            code = block.get_plain_text()
            syntax = Syntax(code, block.language, theme="monokai", line_numbers=True)
            console.print(f"{indent}  {syntax}")
            
            if block.caption:
                caption_text = ''.join(caption.plain_text for caption in block.caption)
                if caption_text:
                    console.print(f"{indent}  [italic]{caption_text}[/italic]")
        elif isinstance(block, TextBlock):
            block_type = f"[bold blue]{block.block_type.value}[/bold blue]"
            text = block.get_plain_text()
            console.print(f"{indent}- {block_type}: {text}")
        else:
            console.print(f"{indent}- [bold yellow]{block.block_type.value}[/bold yellow]")
        
        # Process children if they exist
        if block.has_children and block.children:
            for child in block.children:
                NotionBlockFormatter.format_as_rich(child, indent_level + 1, console)