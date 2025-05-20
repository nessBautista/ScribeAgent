from langflow.custom import Component
from langflow.io import MessageTextInput, Output, HandleInput
from langflow.schema import Data
from langflow.schema.message import Message
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
import tempfile
import os
import json
import re
import ast
from typing import Dict, List, Any, Optional, Union

class PlotlyVisualizerComponent(Component):
    display_name = "Plotly Visualizer"
    description = "Creates dashboard visualizations from structured JSON data with user response"
    icon = "chart-bar"
    name = "PlotlyVisualizerComponent"

    inputs = [
        HandleInput(
            name="structured_data",
            display_name="Structured Data",
            info="The structured data from a StructuredOutput component or CSV agent response",
            input_types=["Data", "Message", "dict", "str"],
            required=True,
        ),
        MessageTextInput(
            name="customize_colors",
            display_name="Customize Colors",
            info="Optional comma-separated colors to use (e.g., 'blue,red,green')",
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    def _extract_json_from_message(self, text):
        """Extract JSON data from text."""
        if not text:
            return None
            
        print(f"Extracting JSON from text: {text[:100]}...") # Show first 100 chars only
        
        # Try to directly parse the text as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Look for JSON in code blocks
        json_code_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_code_pattern, text, re.DOTALL)
        
        for json_str in matches:
            try:
                return json.loads(json_str.strip())
            except json.JSONDecodeError:
                continue
                
        # Look for any JSON object in the text
        json_pattern = r'(\{[\s\S]*?\})'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
                
        return None

    def _safely_get_attr_or_dict_val(self, obj, key, default=None):
        """Safely get a value from an object or dictionary."""
        # If obj is a dictionary
        if isinstance(obj, dict):
            return obj.get(key, default)
        
        # If obj is an object with attributes
        try:
            return getattr(obj, key, default)
        except (AttributeError, TypeError):
            pass
        
        # If obj has a __dict__ attribute (like some message objects)
        try:
            if hasattr(obj, '__dict__'):
                obj_dict = obj.__dict__
                if isinstance(obj_dict, dict) and key in obj_dict:
                    return obj_dict[key]
        except (AttributeError, TypeError):
            pass
            
        # If obj has a 'dict' method (like some Pydantic models)
        try:
            if hasattr(obj, 'dict') and callable(getattr(obj, 'dict')):
                obj_dict = obj.dict()
                if isinstance(obj_dict, dict) and key in obj_dict:
                    return obj_dict[key]
        except (AttributeError, TypeError):
            pass
        
        # Default case - try to access as dictionary (will raise appropriate error if impossible)
        try:
            return obj[key]
        except (KeyError, TypeError):
            return default

    def _extract_dashboard_from_tool_calls(self, data):
        """Extract dashboard data from tool calls structure."""
        if not isinstance(data, dict) and not hasattr(data, '__dict__'):
            return None
            
        # Extract from Messages structure
        messages = self._safely_get_attr_or_dict_val(data, "messages", [])
        if not messages:
            return None
            
        for message in messages:
            # Look for tool_calls in the message
            tool_calls = self._safely_get_attr_or_dict_val(message, "tool_calls", [])
            
            # If no direct tool_calls, try additional_kwargs
            if not tool_calls:
                additional_kwargs = self._safely_get_attr_or_dict_val(message, "additional_kwargs", {})
                tool_calls = self._safely_get_attr_or_dict_val(additional_kwargs, "tool_calls", [])
            
            # Process tool calls if found
            for tool_call in tool_calls:
                # Try to get 'args' - could be attribute or dictionary key
                args = self._safely_get_attr_or_dict_val(tool_call, "args", {})
                
                # Check if dashboard is directly in args
                if "dashboard" in args:
                    return args["dashboard"]
                
                # Check for direct response/visualization structure in args
                if "response" in args and "visualization" in args:
                    return args
                    
                # Check for nested structures in args values
                for key, value in args.items() if isinstance(args, dict) else []:
                    if isinstance(value, dict) and "response" in value and "visualization" in value:
                        return value
            
            # Also try direct content as a fallback
            content = self._safely_get_attr_or_dict_val(message, "content", "")
            if isinstance(content, str) and content:
                try:
                    content_json = json.loads(content)
                    if isinstance(content_json, dict):
                        # Check for dashboard structure
                        if "response" in content_json and "visualization" in content_json:
                            return content_json
                except json.JSONDecodeError:
                    pass
        
        return None

    def _process_dashboard_data(self, data):
        """Process data for the new dashboard schema."""
        if not data:
            return None
            
        # Check if this is already in the dashboard schema format
        if isinstance(data, dict) or hasattr(data, '__dict__'):
            # First, try to extract from tool calls structure
            tool_calls_result = self._extract_dashboard_from_tool_calls(data)
            if tool_calls_result:
                print("Successfully extracted dashboard data from tool calls")
                return tool_calls_result
                
            # If visualization and response are present, this is likely our format
            if self._safely_get_attr_or_dict_val(data, "visualization") and self._safely_get_attr_or_dict_val(data, "response"):
                return data
                
            # If data structure matches, but it's under results
            results = self._safely_get_attr_or_dict_val(data, "results")
            if results and isinstance(results, dict):
                if self._safely_get_attr_or_dict_val(results, "visualization") and self._safely_get_attr_or_dict_val(results, "response"):
                    return results
                    
            # If the data is in a different key
            for key, value in data.items() if isinstance(data, dict) else []:
                if isinstance(value, dict) or hasattr(value, '__dict__'):
                    # Check if this is the dashboard format
                    if self._safely_get_attr_or_dict_val(value, "response") and self._safely_get_attr_or_dict_val(value, "visualization"):
                        return value
                        
                    # Try to extract from tool calls within this value
                    tool_calls_result = self._extract_dashboard_from_tool_calls(value)
                    if tool_calls_result:
                        print(f"Successfully extracted dashboard data from tool calls in {key}")
                        return tool_calls_result
                    
            # Dashboard may be found in the visualization key
            visualization = self._safely_get_attr_or_dict_val(data, "visualization")
            if visualization and isinstance(visualization, dict):
                # Check if the full structure is under visualization
                if self._safely_get_attr_or_dict_val(visualization, "response"):
                    return visualization
                
                # Sometimes the visualization only contains the dashboard part
                if self._safely_get_attr_or_dict_val(visualization, "dashboard"):
                    # Check if response is at the top level
                    if self._safely_get_attr_or_dict_val(data, "response"):
                        return data  # Full structure at top level
                        
            # Or it might be that we have incomplete data structure
            if self._safely_get_attr_or_dict_val(data, "dashboard") or self._safely_get_attr_or_dict_val(data, "plots"):
                # Try to piece together a complete structure
                dashboard_data = {
                    "response": self._safely_get_attr_or_dict_val(data, "response", {
                        "answer": "Data analysis results",
                        "summary": "Visualization generated from data",
                        "additional_insights": [],
                        "recommendations": []
                    }),
                    "visualization": {
                        "has_plots": True,
                        "display_mode": "dashboard",
                        "dashboard": self._safely_get_attr_or_dict_val(data, "dashboard", {})
                    },
                    "metadata": self._safely_get_attr_or_dict_val(data, "metadata", {})
                }
                
                # If plots are at the top level, move them to dashboard
                plots = self._safely_get_attr_or_dict_val(data, "plots")
                if plots and self._safely_get_attr_or_dict_val(dashboard_data["visualization"], "dashboard"):
                    dashboard_data["visualization"]["dashboard"]["plots"] = plots
                    
                return dashboard_data
                
        return None

    def build_output(self) -> Message:
        # Process the input data
        print(f"--------------->structured_data:{self.structured_data}")
        data_source = self.structured_data
        dashboard_data = None
        
        # Log input type for debugging
        print(f"Input data type: {type(data_source)}")
        if isinstance(data_source, Message):
            print(f"Message text sample: {data_source.text[:100]}...")
        elif isinstance(data_source, Data):
            data_dict = data_source.data
            print(f"Data object keys: {data_dict.keys() if isinstance(data_dict, dict) else 'Not a dict'}")
        
        # Handle different types of input
        try:
            if isinstance(data_source, Data):
                # Extract data from Data object
                data_dict = data_source.data
                
                # Try to process as dashboard data
                dashboard_data = self._process_dashboard_data(data_dict)
                
                # If not in dashboard format, try to extract JSON
                text_key = self._safely_get_attr_or_dict_val(data_dict, "text_key")
                if not dashboard_data and text_key and text_key in data_dict:
                    text_content = data_dict[text_key]
                    if isinstance(text_content, str):
                        extracted_json = self._extract_json_from_message(text_content)
                        dashboard_data = self._process_dashboard_data(extracted_json)
                
                # Try to extract from results if it exists
                if not dashboard_data:
                    results = self._safely_get_attr_or_dict_val(data_dict, "results")
                    if results:
                        dashboard_data = self._process_dashboard_data(results)
                    
            elif isinstance(data_source, Message):
                # Try to extract JSON from message text
                extracted_json = self._extract_json_from_message(data_source.text)
                dashboard_data = self._process_dashboard_data(extracted_json)
                
            elif isinstance(data_source, dict):
                # Try to process dict directly
                dashboard_data = self._process_dashboard_data(data_source)
                
            elif isinstance(data_source, str):
                # Try to extract JSON from string
                extracted_json = self._extract_json_from_message(data_source)
                dashboard_data = self._process_dashboard_data(extracted_json)
            
            # Debugging information
            if dashboard_data:
                if isinstance(dashboard_data, dict):
                    print(f"Dashboard data found with keys: {dashboard_data.keys()}")
                else:
                    print(f"Dashboard data found but is not a dict. Type: {type(dashboard_data)}")
            
            # Check if we have valid dashboard data
            if not dashboard_data:
                fallback_data = None
                
                # If we have a dict but not in dashboard format, try to use legacy format
                if isinstance(data_source, dict) or (isinstance(data_source, Data) and isinstance(data_source.data, dict)):
                    data_to_check = data_source.data if isinstance(data_source, Data) else data_source
                    
                    # Check for legacy plotly format
                    if isinstance(data_to_check, dict) and "plot_type" in data_to_check and "data" in data_to_check:
                        fallback_data = data_to_check
                
                # If we found legacy data, adapt it to the new format
                if fallback_data:
                    print("Using legacy format and adapting to dashboard schema")
                    dashboard_data = {
                        "response": {
                            "answer": "Data visualization generated from legacy format",
                            "summary": "Visualization created from plotly data",
                            "additional_insights": [],
                            "recommendations": []
                        },
                        "visualization": {
                            "has_plots": True,
                            "display_mode": "single",
                            "dashboard": {
                                "title": self._safely_get_attr_or_dict_val(fallback_data.get("layout", {}), "title", "Data Visualization"),
                                "auto_layout": True,
                                "plots": [{
                                    "id": "plot1",
                                    "title": self._safely_get_attr_or_dict_val(fallback_data.get("layout", {}), "title", "Visualization"),
                                    "importance": 1,
                                    "plot_type": fallback_data.get("plot_type", "bar"),
                                    "data": fallback_data.get("data", []),
                                    "layout": fallback_data.get("layout", {})
                                }]
                            }
                        },
                        "metadata": {
                            "generated_plots": 1
                        }
                    }
                else:
                    return Message(
                        text="Error: Could not extract valid dashboard data from the input. Please check that your data follows the required schema.",
                        sender="Bot",
                    )
            
            return self._create_dashboard_message(dashboard_data)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return Message(
                text=f"Error processing dashboard data: {str(e)}\n\nTraceback:\n{error_trace}",
                sender="Bot",
            )

    def _format_text_response(self, response_data):
        """Format the text response part of the dashboard."""
        if not response_data:
            return "No response data available."
            
        text_parts = []
        
        # Add the main answer
        answer = self._safely_get_attr_or_dict_val(response_data, "answer")
        if answer:
            text_parts.append(f"**{answer}**\n")
        
        # Add the summary
        summary = self._safely_get_attr_or_dict_val(response_data, "summary")
        if summary:
            text_parts.append(f"{summary}\n")
        
        # Add additional insights
        insights = self._safely_get_attr_or_dict_val(response_data, "additional_insights", [])
        if insights:
            text_parts.append("\n**Additional Insights:**")
            for insight in insights:
                text_parts.append(f"- {insight}")
            text_parts.append("")
        
        # Add recommendations
        recommendations = self._safely_get_attr_or_dict_val(response_data, "recommendations", [])
        if recommendations:
            text_parts.append("**Recommendations:**")
            for recommendation in recommendations:
                text_parts.append(f"- {recommendation}")
        
        return "\n".join(text_parts)
    
    def _determine_trace_types(self, plots):
        """Determine the trace types for each plot to create proper subplot specs."""
        trace_types = []
        for plot in plots:
            # Default to 'xy' for most plot types
            plot_type = 'xy'
            
            # Check if this is a pie chart
            data_items = self._safely_get_attr_or_dict_val(plot, "data", [])
            for item in data_items:
                item_type = self._safely_get_attr_or_dict_val(item, "type")
                plot_plot_type = self._safely_get_attr_or_dict_val(plot, "plot_type")
                
                if item_type == "pie" or (not item_type and plot_plot_type == "pie"):
                    plot_type = 'domain'
                    break
            
            trace_types.append(plot_type)
        
        return trace_types

    def _create_dashboard_message(self, dashboard_data):
        """Create a message with text response and dashboard visualization."""
        try:
            # Extract components
            response_data = self._safely_get_attr_or_dict_val(dashboard_data, "response", {})
            visualization_data = self._safely_get_attr_or_dict_val(dashboard_data, "visualization", {})
            metadata = self._safely_get_attr_or_dict_val(dashboard_data, "metadata", {})
            
            # Format the text response
            text_response = self._format_text_response(response_data)
            
            # Check if visualization is enabled
            has_plots = self._safely_get_attr_or_dict_val(visualization_data, "has_plots", True)
            if not has_plots:
                # If no plots, just return the text response
                return Message(
                    text=text_response,
                    sender="Bot",
                )
            
            # Get dashboard data
            dashboard = self._safely_get_attr_or_dict_val(visualization_data, "dashboard", {})
            plots = self._safely_get_attr_or_dict_val(dashboard, "plots", [])
            
            if not plots:
                # If no plots defined, just return the text response
                return Message(
                    text=text_response,
                    sender="Bot",
                )
            
            # Sort plots by importance
            plots = sorted(plots, key=lambda x: self._safely_get_attr_or_dict_val(x, "importance", 999))
            
            # Get dashboard title and subtitle
            dashboard_title = self._safely_get_attr_or_dict_val(dashboard, "title", "Data Dashboard")
            dashboard_subtitle = self._safely_get_attr_or_dict_val(dashboard, "subtitle", "")
            
            # Determine layout based on number of plots
            num_plots = len(plots)
            
            # Apply custom colors if provided
            custom_colors = None
            if hasattr(self, 'customize_colors') and self.customize_colors:
                custom_colors = [color.strip() for color in self.customize_colors.split(',')]
                print(f"Using custom colors: {custom_colors}")
            
            # Create figure with appropriate subplot configuration
            if num_plots == 1:
                # Single plot
                fig = go.Figure()
                self._add_traces_to_figure(fig, plots[0], custom_colors)
                
                # Extract layout without the title to avoid conflicts
                plot_layout = self._safely_get_attr_or_dict_val(plots[0], "layout", {}).copy() if self._safely_get_attr_or_dict_val(plots[0], "layout") else {}
                if "title" in plot_layout:
                    del plot_layout["title"]  # Remove title from layout to avoid conflict
                
                # Apply the layout with the title separately
                fig.update_layout(
                    title=self._safely_get_attr_or_dict_val(plots[0], "title", "Visualization"),
                    **plot_layout
                )
            else:
                # Multiple plots - first determine trace types for compatible subplot configuration
                trace_types = self._determine_trace_types(plots)
                
                if num_plots <= 2:
                    # Two plots: vertical arrangement
                    fig = make_subplots(
                        rows=2, cols=1, 
                        subplot_titles=[self._safely_get_attr_or_dict_val(plot, "title", f"Plot {i+1}") for i, plot in enumerate(plots[:2])],
                        vertical_spacing=0.15,
                        specs=[[{"type": trace_types[0]}], [{"type": trace_types[1 if len(trace_types) > 1 else 0]}]]
                    )
                    for i, plot in enumerate(plots[:2]):
                        self._add_traces_to_figure(fig, plot, custom_colors, row=i+1, col=1)
                
                elif num_plots <= 4:
                    # 3-4 plots: 2x2 grid
                    specs = [
                        [{"type": trace_types[0]}, {"type": trace_types[1] if len(trace_types) > 1 else trace_types[0]}],
                        [{"type": trace_types[2] if len(trace_types) > 2 else trace_types[0]}, {"type": trace_types[3] if len(trace_types) > 3 else trace_types[0]}]
                    ]
                    
                    fig = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=[self._safely_get_attr_or_dict_val(plot, "title", f"Plot {i+1}") for i, plot in enumerate(plots[:4])],
                        vertical_spacing=0.15,
                        horizontal_spacing=0.08,
                        specs=specs
                    )
                    positions = [(1,1), (1,2), (2,1), (2,2)]
                    for i, plot in enumerate(plots[:4]):
                        row, col = positions[i]
                        self._add_traces_to_figure(fig, plot, custom_colors, row=row, col=col)
                
                # Update overall layout
                fig.update_layout(
                    title=f"{dashboard_title}{' - ' + dashboard_subtitle if dashboard_subtitle else ''}",
                    showlegend=False,
                    height=min(350 * ((num_plots + 1) // 2), 1200),  # Scale height based on number of plots
                    margin={"t": 50, "b": 20, "l": 20, "r": 20},
                    paper_bgcolor="white"
                )
            
            # Save plot to a temporary file
            temp_dir = tempfile.gettempdir()
            file_name = f"dashboard_{hash(str(dashboard_data))}.png"
            img_path = os.path.join(temp_dir, file_name)
            
            print(f"Generating dashboard image...")
            
            # Write the image to the file
            fig.write_image(img_path)
            
            # Create a base64 version as well
            img_bytes = fig.to_image(format="png")
            base64_url = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
            
            # Create the markdown with the text response and embedded image
            markdown_text = f"{text_response}\n\n![{dashboard_title}]({base64_url})"
            
            print(f"Successfully created dashboard for: {dashboard_title}")
            
            # Create the message
            message = Message(
                text=markdown_text,
                sender="Bot",
            )
            
            return message
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error creating dashboard: {error_trace}")
            # Fallback to returning an error with the dashboard data if we can't generate an image
            return Message(
                text=f"Error generating dashboard: {str(e)}\n\nTraceback:\n{error_trace}\n\nResponse text:\n{self._format_text_response(dashboard_data)}",
                sender="Bot",
            )
    
    def _add_traces_to_figure(self, fig, plot_data, custom_colors=None, row=None, col=None):
        """Add traces from a plot definition to a figure."""
        plot_type = self._safely_get_attr_or_dict_val(plot_data, "plot_type", "bar")
        data_items = self._safely_get_attr_or_dict_val(plot_data, "data", [])
        
        for i, item in enumerate(data_items):
            trace_type = self._safely_get_attr_or_dict_val(item, "type", plot_type)
            
            # Get x and y values
            x_values = self._safely_get_attr_or_dict_val(item, "x", [])
            y_values = self._safely_get_attr_or_dict_val(item, "y", [])
            
            # Get labels and values for pie charts
            labels = self._safely_get_attr_or_dict_val(item, "labels", [])
            values = self._safely_get_attr_or_dict_val(item, "values", [])
            
            # Prepare marker properties
            base_marker = self._safely_get_attr_or_dict_val(item, "marker", {})
            
            # Use custom colors if available
            if custom_colors and i < len(custom_colors):
                marker_color = custom_colors[i]
                if isinstance(base_marker, dict):
                    base_marker["color"] = marker_color
                else:
                    base_marker = {"color": marker_color}
            
            # Create the trace based on type
            if trace_type == "bar":
                trace = go.Bar(
                    x=x_values,
                    y=y_values,
                    name=self._safely_get_attr_or_dict_val(item, "name", f"Series {i+1}"),
                    marker=base_marker,
                    orientation=self._safely_get_attr_or_dict_val(item, "orientation", "v"),
                )
            elif trace_type == "line":
                trace = go.Scatter(
                    x=x_values,
                    y=y_values,
                    name=self._safely_get_attr_or_dict_val(item, "name", f"Series {i+1}"),
                    mode=self._safely_get_attr_or_dict_val(item, "mode", "lines"),
                    marker=base_marker,
                    line=self._safely_get_attr_or_dict_val(item, "line", {}),
                    fill=self._safely_get_attr_or_dict_val(item, "fill"),
                    fillcolor=self._safely_get_attr_or_dict_val(item, "fillcolor"),
                )
            elif trace_type == "area":
                trace = go.Scatter(
                    x=x_values,
                    y=y_values,
                    name=self._safely_get_attr_or_dict_val(item, "name", f"Series {i+1}"),
                    mode=self._safely_get_attr_or_dict_val(item, "mode", "lines"),
                    marker=base_marker,
                    line=self._safely_get_attr_or_dict_val(item, "line", {}),
                    fill="tozeroy",
                    fillcolor=self._safely_get_attr_or_dict_val(item, "fillcolor", "rgba(100, 100, 255, 0.3)"),
                )
            elif trace_type == "scatter":
                trace = go.Scatter(
                    x=x_values,
                    y=y_values,
                    name=self._safely_get_attr_or_dict_val(item, "name", f"Series {i+1}"),
                    mode=self._safely_get_attr_or_dict_val(item, "mode", "markers"),
                    marker=base_marker,
                )
            elif trace_type == "pie":
                trace = go.Pie(
                    labels=labels,
                    values=values,
                    name=self._safely_get_attr_or_dict_val(item, "name", f"Series {i+1}"),
                    marker=base_marker,
                )
            else:
                continue  # Skip unknown trace types
            
            # Add the trace to the figure
            if row is not None and col is not None:
                fig.add_trace(trace, row=row, col=col)
            else:
                fig.add_trace(trace)