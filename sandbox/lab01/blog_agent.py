#!/usr/bin/env python3

# /// script
# dependencies = [
#   "anthropic>=0.45.2",
#   "rich>=13.7.0",
#   "python-dotenv",
#   "requests>=2.31.0"
# ]
# ///

"""
/// Example Usage

# Run blog agent with default compute loops (6)
uv run blog_agent.py -p "Write a blog post about the history of coffee"

# Run with custom compute loops
uv run blog_agent.py -p "Write a blog post about space exploration" -c 8

///
"""

import os
import sys
import json
import argparse
from typing import List
from rich.console import Console
from rich.panel import Panel
from anthropic import Anthropic
import dotenv
import requests
from blog_task import BlogTask


# Initialize rich console
console = Console()

def read_recommendations(reasoning: str) -> str:
    """Reads the recommendations document that contains guidelines for writing blog posts.
    Args:
        reasoning: Explanation of why we need to read recommendations for writing the blog post
    Returns:
        String containing the recommendations content or error message
    """
    try:
        recommendations_path = os.path.join("resources", "recommendations.md")
        with open(recommendations_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        error_msg = f"Error reading recommendations: {str(e)}"
        console.print(f"[yellow]Warning: {error_msg}[/yellow]")
        return "No recommendations available"

# Update the AGENT_PROMPT to include the new tool
AGENT_PROMPT = """<purpose>
    You are an expert blog post writer and editor. Your goal is to create engaging and informative content
    on any topic requested by the user, and then enhance it with editorial improvements and rich media suggestions.
</purpose>

<instructions>
    <instruction>Write a blog post that matches the user's requirements.</instruction>
    <instruction>Include a clear title that captures the main topic.</instruction>
    <instruction>Organize the content with proper structure and flow.</instruction>
    <instruction>Use the read_recommendations tool to get writing guidelines.</instruction>
    
    <instruction>After writing the initial draft, switch to editor mode:</instruction>
    <sub-instructions>
        <instruction>Review the content for clarity, engagement, and impact.</instruction>
        <instruction>Add editorial comments prefixed with "EDITOR:" to suggest improvements.</instruction>
        <instruction>Recommend strategic placement of rich media enhancements:</instruction>
        <list>
            - Images: Describe desired content and purpose (e.g., "IMAGE: Add a diagram showing the coffee brewing process to illustrate the steps")
            - Code blocks: Suggest relevant code examples with context
            - URLs: Recommend authoritative sources and references
            - Quotes: Suggest impactful quotes from experts or sources
            - Charts/Graphs: Describe data visualizations that would enhance understanding
        </list>
        <instruction>Each enhancement suggestion should include:</instruction>
        <list>
            - Clear placement indication (where in the content)
            - Description of the content
            - Explanation of why it enhances the post
        </list>
    </sub-instructions>

    <instruction>When satisfied with both content and enhancements, save it using the write_blog_post tool.</instruction>
    <instruction>The filename should be a clean, URL-friendly version of the title.</instruction>
</instructions>

<tools>
    <tool>
        <name>read_recommendations</name>
        <description>Reads writing recommendations and guidelines</description>
        <parameters>
            <parameter>
                <name>reasoning</name>
                <type>string</type>
                <description>Explanation of why we need to read recommendations for writing the blog post</description>
                <required>true</required>
            </parameter>
        </parameters>
    </tool>
    <tool>
        <name>write_blog_post</name>
        <description>Saves the blog post to a file</description>
        <parameters>
            <parameter>
                <name>reasoning</name>
                <type>string</type>
                <description>Explanation of how the post meets requirements</description>
                <required>true</required>
            </parameter>
            <parameter>
                <name>title</name>
                <type>string</type>
                <description>Title of the blog post</description>
                <required>true</required>
            </parameter>
            <parameter>
                <name>content</name>
                <type>string</type>
                <description>Full content of the blog post</description>
                <required>true</required>
            </parameter>
            <parameter>
                <name>filename</name>
                <type>string</type>
                <description>Name of the file to save the post</description>
                <required>true</required>
            </parameter>
        </parameters>
    </tool>
</tools>

<user-request>
    {{user_request}}
</user-request>
"""

def write_blog_post(reasoning: str, title: str, content: str, filename: str) -> str:
    """Saves a blog post to the filesystem in the drafts folder.

    Args:
        reasoning: Explanation of how the post meets requirements
        title: The title of the blog post
        content: The full content of the blog post
        filename: Name of the file to save the post

    Returns:
        String indicating success or failure
    """
    try:
        # Validate all required parameters
        if not all([reasoning, title, content, filename]):
            missing_params = [
                param for param, value in {
                    'reasoning': reasoning,
                    'title': title,
                    'content': content,
                    'filename': filename
                }.items() if not value
            ]
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

        # Ensure filename has .md extension
        if not filename.endswith('.md'):
            filename += '.md'
            
        # Create drafts directory if it doesn't exist
        drafts_dir = os.path.join(os.path.dirname(__file__), 'drafts')
        os.makedirs(drafts_dir, exist_ok=True)
        
        # Create full file path in drafts directory
        filepath = os.path.join(drafts_dir, filename)
        
        # Create blog post with markdown formatting
        blog_content = f"""# {title}

{content}
"""
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write(blog_content)
            
        console.print(f"[green]Successfully saved blog post to {filepath}[/green]")
        return f"Blog post saved to {filepath}"
    except Exception as e:
        error_msg = f"Error saving blog post: {str(e)}"
        console.print(f"[red]{error_msg}[/red]")
        return error_msg

def get_blog_task() -> str:
    """Fetch blog task content from Linear and Notion."""
    blog_task = BlogTask()
    return blog_task.get_task()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Blog Post Writing Agent using Claude")
    parser.add_argument(
        "-p", "--prompt", 
        help="Optional: Override Linear task with custom blog post request",
        default=None
    )
    parser.add_argument(
        "-c",
        "--compute",
        type=int,
        default=6,
        help="Maximum number of agent loops (default: 6)",
    )
    args = parser.parse_args()

    # Configure the API keys
    dotenv.load_dotenv()
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if not ANTHROPIC_API_KEY:
        console.print("[red]Error: ANTHROPIC_API_KEY environment variable is not set[/red]")
        console.print("Please get your API key from your Anthropic dashboard")
        console.print("Then set it with: export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Get blog post requirements - either from Linear or command line
    if not args.prompt:
        console.print("[yellow]Fetching task from Linear and Notion...[/yellow]")
        try:
            task_content = get_blog_task()
            blog_prompt = f"User's requirements:\n{task_content}"
            console.print(Panel(f"[green]Using Task Content:[/green]\n{blog_prompt}"))
        except Exception as e:
            console.print(f"[red]Error fetching task: {str(e)}[/red]")
            sys.exit(1)
    else:
        blog_prompt = args.prompt

    # Initialize Anthropic client
    client = Anthropic()

    # Create the full prompt
    completed_prompt = AGENT_PROMPT.replace("{{user_request}}", blog_prompt)
    messages = [{"role": "user", "content": completed_prompt}]

    compute_iterations = 0

    # Main agent loop
    while True:
        console.rule(f"[yellow]Agent Loop {compute_iterations+1}/{args.compute}[/yellow]")
        compute_iterations += 1

        if compute_iterations >= args.compute:
            console.print("[yellow]Warning: Reached maximum compute loops without saving post[/yellow]")
            raise Exception(f"Maximum compute loops reached: {compute_iterations}/{args.compute}")

        try:
            # Add the user's initial prompt if this is the first iteration
            if compute_iterations == 1:
                messages.append({
                    "role": "user", 
                    "content": [{"type": "text", "text": blog_prompt}]
                })
                # console.print(Panel(f"[green]Initial interaction:[/green]\n{messages}"))

            # Generate content with tool support
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,  # Increased to allow for longer blog content
                messages=messages,
                tools=[
                    {
                        "name": "read_recommendations",
                        "description": "Reads writing recommendations and guidelines",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "reasoning": {
                                    "type": "string",
                                    "description": "Explanation of why we need to read recommendations for writing the blog post",
                                }
                            },
                            "required": ["reasoning"],
                        },
                    },
                    {
                        "name": "write_blog_post",
                        "description": "Saves the blog post to a file",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "reasoning": {
                                    "type": "string",
                                    "description": "Explanation of how the post meets requirements",
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Title of the blog post",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Full content of the blog post",
                                },
                                "filename": {
                                    "type": "string",
                                    "description": "Name of the file to save the post",
                                },
                            },
                            "required": ["reasoning", "title", "content", "filename"],
                        },
                    }
                ],
                tool_choice={"type": "any"},  # Always force a tool call
            )

            # Look for tool calls in the response
            tool_calls = []

            for block in response.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    tool_calls.append(block)

            if tool_calls:
                for tool_call in tool_calls:
                    tool_use_id = tool_call.id
                    func_name = tool_call.name
                    func_args = tool_call.input  # already a dict; no need to call json.loads

                    console.print(
                        f"[blue]Tool Call:[/blue] {func_name}({json.dumps(func_args)})"
                    )

                    messages.append({"role": "assistant", "content": response.content})

                    try:
                        if func_name == "write_blog_post":
                            result = write_blog_post(
                                reasoning=func_args["reasoning"],
                                title=func_args["title"],
                                content=func_args["content"],
                                filename=func_args["filename"]
                            )
                            console.print(f"\n[green]Blog Post Saved![/green]")
                            console.print(Panel(
                                f"[green]Blog Post Written[/green]\nReasoning: {func_args['reasoning']}\nTitle: {func_args['title']}\nFile: {func_args['filename']}"
                            ))
                            return
                        elif func_name == "read_recommendations":
                            result = read_recommendations(
                                reasoning=func_args["reasoning"]
                            )
                        else:
                            raise Exception(f"Unknown tool call: {func_name}")

                        # Add tool result as user message with proper format
                        messages.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": tool_use_id,
                                        "content": str(result)
                                    }
                                ]
                            }
                        )

                    except Exception as e:
                        error_msg = f"Error executing {func_name}: {str(e)}"
                        console.print(f"[red]{error_msg}[/red]")
                        # Add error as user message with proper format
                        messages.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": tool_use_id,
                                        "content": error_msg
                                    }
                                ]
                            }
                        )
                        continue

            else:
                raise Exception("No tool calls found in response - should never happen")

        except Exception as e:
            console.print(f"[red]Error in agent loop: {str(e)}[/red]")
            raise e

if __name__ == "__main__":    
    main()