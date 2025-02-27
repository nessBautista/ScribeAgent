#!/usr/bin/env python3

# /// script
# dependencies = [
#   "rich>=13.7.0",
# ]
# ///

"""
/// Example Usage

# Run the script with uv
uv run hello_world.py

# Run with a name parameter
uv run hello_world.py --name "Alice"

///
"""

import argparse
from rich.console import Console
from rich.panel import Panel

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="UV Hello World Example")
    parser.add_argument(
        "--name",
        default="World",
        help="Name to greet (default: World)"
    )
    args = parser.parse_args()

    # Initialize rich console
    console = Console()

    # Create a fancy greeting
    greeting = f"Hello, {args.name}!"
    
    # Display the greeting in a panel with some styling
    console.print(
        Panel(
            f"[bold blue]{greeting}[/bold blue]",
            title="Greeting",
            border_style="green"
        )
    )

if __name__ == "__main__":
    main()