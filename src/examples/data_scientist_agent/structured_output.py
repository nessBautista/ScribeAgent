from pydantic import BaseModel, Field, create_model
from trustcall import create_extractor
import json
from typing import List, Union, Dict, Any, Optional

from langflow.base.models.chat_result import get_chat_result
from langflow.custom import Component
from langflow.helpers.base_model import build_model_from_schema
from langflow.io import (
    BoolInput,
    HandleInput,
    MessageTextInput,
    MultilineInput,
    Output,
    TableInput,
    DropdownInput,
)
from langflow.schema.data import Data
from langflow.schema.dataframe import DataFrame
from langflow.schema.table import EditMode


class StructuredOutputComponent(Component):
    display_name = "Structured Output"
    description = (
        "Transforms LLM responses into **structured data formats**. Ideal for extracting specific information "
        "or creating consistent outputs."
    )
    name = "StructuredOutput"
    icon = "braces"

    inputs = [
        HandleInput(
            name="llm",
            display_name="Language Model",
            info="The language model to use to generate the structured output.",
            input_types=["LanguageModel"],
            required=True,
        ),
        MessageTextInput(
            name="input_value",
            display_name="Input Message",
            info="The input message to the language model.",
            tool_mode=True,
            required=True,
        ),
        DropdownInput(
            name="output_type",
            display_name="Output Type",
            info="Select the type of structured output to generate",
            options=["Custom Schema", "Dashboard Visualization"],
            value="Custom Schema",
            required=True,
        ),
        MultilineInput(
            name="custom_schema_system_prompt",
            display_name="Custom Schema Instructions",
            info="The instructions to the language model for formatting the custom schema output.",
            value=(
                "You are an AI system designed to extract structured information from unstructured text."
                "Given the input_text, return a JSON object with predefined keys based on the expected structure."
                "Extract values accurately and format them according to the specified type "
                "(e.g., string, integer, float, date)."
                "If a value is missing or cannot be determined, return a default "
                "(e.g., null, 0, or 'N/A')."
                "If multiple instances of the expected structure exist within the input_text, "
                "stream each as a separate JSON object."
            ),
            required=False,
            advanced=False,
        ),
        MessageTextInput(
            name="schema_name",
            display_name="Schema Name",
            info="Provide a name for the output data schema.",
            advanced=True,
        ),
        TableInput(
            name="output_schema",
            display_name="Custom Output Schema",
            info="Define the structure and data types for the model's output when using Custom Schema.",
            required=False,
            table_schema=[
                {
                    "name": "name",
                    "display_name": "Name",
                    "type": "str",
                    "description": "Specify the name of the output field.",
                    "default": "field",
                    "edit_mode": EditMode.INLINE,
                },
                {
                    "name": "description",
                    "display_name": "Description",
                    "type": "str",
                    "description": "Describe the purpose of the output field.",
                    "default": "description of field",
                    "edit_mode": EditMode.POPOVER,
                },
                {
                    "name": "type",
                    "display_name": "Type",
                    "type": "str",
                    "edit_mode": EditMode.INLINE,
                    "description": (
                        "Indicate the data type of the output field (e.g., str, int, float, bool, list, dict)."
                    ),
                    "options": ["str", "int", "float", "bool", "list", "dict"],
                    "default": "str",
                },
                {
                    "name": "multiple",
                    "display_name": "Multiple",
                    "type": "boolean",
                    "description": "Set to True if this output field should be a list of the specified type.",
                    "default": "False",
                    "edit_mode": EditMode.INLINE,
                },
            ],
            value=[
                {
                    "name": "field",
                    "description": "description of field",
                    "type": "str",
                    "multiple": "False",
                }
            ],
        ),
        MultilineInput(
            name="dashboard_schema_instructions",
            display_name="Dashboard Schema Instructions",
            info="Instructions for the language model on how to format the dashboard visualization data.",
            value=(
                "You are an AI system designed to analyze data and generate dashboard visualizations.\n\n"
                "Given the user's input, create a JSON object following this structure:\n\n"
                "{\n"
                '  "response": {\n'
                '    "answer": "Your direct answer to the user\'s question",\n'
                '    "summary": "A brief summary of key insights",\n'
                '    "additional_insights": ["Insight 1", "Insight 2"],\n'
                '    "recommendations": ["Recommendation 1", "Recommendation 2"]\n'
                "  },\n"
                '  "visualization": {\n'
                '    "has_plots": true,\n'
                '    "display_mode": "dashboard",\n'
                '    "dashboard": {\n'
                '      "title": "Dashboard Title",\n'
                '      "subtitle": "Optional subtitle with metrics",\n'
                '      "auto_layout": true,\n'
                '      "plots": [\n'
                "        {\n"
                '          "id": "plot1",\n'
                '          "title": "Plot Title",\n'
                '          "description": "Plot description",\n'
                '          "importance": 1,\n'
                '          "plot_type": "bar|line|area|pie|scatter",\n'
                '          "data": [\n'
                "            {\n"
                '              "x": ["Category A", "Category B"],\n'
                '              "y": [value1, value2],\n'
                '              "type": "bar|line|area|pie|scatter"\n'
                "            }\n"
                "          ],\n"
                '          "layout": {\n'
                '            "height": 300,\n'
                '            "xaxis": {"title": "X-Axis Title"},\n'
                '            "yaxis": {"title": "Y-Axis Title"}\n'
                "          }\n"
                "        }\n"
                "      ]\n"
                "    }\n"
                "  },\n"
                '  "metadata": {\n'
                '    "total_records": number,\n'
                '    "time_period": "Period covered by data",\n'
                '    "data_sources": ["source1", "source2"],\n'
                '    "query_info": {\n'
                '      "original_query": "User\'s original question",\n'
                '      "generated_plots": number\n'
                "    }\n"
                "  }\n"
                "}\n\n"
                "Important guidelines:\n"
                "- Add 1-4 visualizations based on what best answers the user's question\n"
                "- Each plot should have a unique ID and descriptive title\n"
                "- For each plot, choose the most appropriate visualization type\n"
                "- Assign importance values (1=highest) to indicate display priority\n"
                "- Include meaningful insights and recommendations in the response section"
            ),
            required=False,
            advanced=False,
        ),
        BoolInput(
            name="multiple",
            advanced=True,
            display_name="Generate Multiple",
            info="[Deprecated] Always set to True",
            value=True,
        ),
    ]

    outputs = [
        Output(
            name="structured_output",
            display_name="Structured Output",
            method="build_structured_output",
        ),
        Output(
            name="structured_output_dataframe",
            display_name="DataFrame",
            method="as_dataframe",
        ),
        Output(
            name="visualization_data",
            display_name="Visualization Data",
            method="get_visualization_data",
        ),
    ]

    def build_structured_output_base(self) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Build structured output based on the selected output type."""
        if self.output_type == "Custom Schema":
            print(f"------------------>Custom Schema:{self._build_dashboard_schema_output}")
            return self._build_dashboard_schema_output()
        elif self.output_type == "Dashboard Visualization":
            print(f"------------------>Dashboard Visualization:{self._build_dashboard_schema_output()}")
            return self._build_dashboard_schema_output()
        else:
            msg = f"Unsupported output type: {self.output_type}"
            raise ValueError(msg)

    def _build_custom_schema_output(self) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Build output for the Custom Schema option."""
        schema_name = self.schema_name or "OutputModel"

        if not hasattr(self.llm, "with_structured_output"):
            msg = "Language model does not support structured output."
            raise TypeError(msg)
        if not self.output_schema:
            msg = "Output schema cannot be empty for Custom Schema output type"
            raise ValueError(msg)

        output_model_ = build_model_from_schema(self.output_schema)

        output_model = create_model(
            schema_name,
            __doc__=f"A list of {schema_name}.",
            objects=(list[output_model_], Field(description=f"A list of {schema_name}.")),  # type: ignore[valid-type]
        )

        try:
            llm_with_structured_output = create_extractor(self.llm, tools=[output_model])
        except NotImplementedError as exc:
            msg = f"{self.llm.__class__.__name__} does not support structured output."
            raise TypeError(msg) from exc
        
        config_dict = {
            "run_name": self.display_name,
            "project_name": self.get_project_name(),
            "callbacks": self.get_langchain_callbacks(),
        }
        
        # Use custom_schema_system_prompt if it exists, otherwise use a default prompt
        system_prompt = self.custom_schema_system_prompt
        if not system_prompt:
            system_prompt = (
                "You are an AI system designed to extract structured information from unstructured text."
                "Given the input_text, return a JSON object with predefined keys based on the expected structure."
                "Extract values accurately and format them according to the specified type."
            )
            
        result = get_chat_result(
            runnable=llm_with_structured_output,
            system_message=system_prompt,
            input_value=self.input_value,
            config=config_dict,
        )
        
        if isinstance(result, BaseModel):
            result = result.model_dump()
        if responses := result.get("responses"):
            result = responses[0].model_dump()
        if result and "objects" in result:
            return result["objects"]

        return result

    def _build_dashboard_schema_output(self) -> Dict[str, Any]:
        """Build output for the Dashboard Visualization option."""
        
        # Define Pydantic models for dashboard schema validation
        class ResponseModel(BaseModel):
            answer: str
            summary: str
            additional_insights: List[str]
            recommendations: List[str]

        class PlotDataItem(BaseModel):
            x: Optional[List[Union[str, int, float]]] = None
            y: Optional[List[Union[str, int, float]]] = None
            orientation: Optional[str] = None
            type: Optional[str] = None
            mode: Optional[str] = None
            marker: Optional[Dict[str, Any]] = None
            fill: Optional[str] = None
            line: Optional[Dict[str, Any]] = None
            fillcolor: Optional[str] = None
            labels: Optional[List[str]] = None
            values: Optional[List[Union[int, float]]] = None

        class PlotLayout(BaseModel):
            height: Optional[int] = None
            width: Optional[int] = None
            margin: Optional[Dict[str, int]] = None
            xaxis: Optional[Dict[str, Any]] = None
            yaxis: Optional[Dict[str, Any]] = None
            title: Optional[str] = None
            plot_bgcolor: Optional[str] = None
            paper_bgcolor: Optional[str] = None

        class PlotResponsive(BaseModel):
            small: Optional[Dict[str, Any]] = None
            large: Optional[Dict[str, Any]] = None

        class Plot(BaseModel):
            id: str
            title: str
            description: Optional[str] = None
            importance: int
            plot_type: str
            data: List[PlotDataItem]
            layout: PlotLayout
            responsive: Optional[PlotResponsive] = None

        class LayoutOptions(BaseModel):
            default: Dict[str, Any]
            single_plot: Optional[Dict[str, Any]] = None
            two_plots: Optional[Dict[str, Any]] = None
            three_plots: Optional[Dict[str, Any]] = None
            four_plots: Optional[Dict[str, Any]] = None
            many_plots: Optional[Dict[str, Any]] = None

        class Dashboard(BaseModel):
            title: str
            subtitle: Optional[str] = None
            auto_layout: Optional[bool] = True
            plots: List[Plot]
            layout_options: Optional[LayoutOptions] = None

        class Visualization(BaseModel):
            has_plots: bool
            display_mode: str
            dashboard: Dashboard

        class QueryInfo(BaseModel):
            original_query: str
            generated_plots: int
            processing_time_ms: Optional[int] = None

        class Metadata(BaseModel):
            total_records: Optional[int] = None
            time_period: Optional[str] = None
            data_sources: Optional[List[str]] = None
            last_updated: Optional[str] = None
            query_info: QueryInfo

        class DashboardVisualizationModel(BaseModel):
            response: ResponseModel
            visualization: Visualization
            metadata: Metadata

        # Create the dashboard visualization model
        dashboard_model = create_model(
            "DashboardVisualization",
            __doc__="Complete dashboard visualization with response, visualization data, and metadata.",
            dashboard=(DashboardVisualizationModel, Field(description="Dashboard visualization with user response and plots"))
        )

        try:
            system_prompt = self.dashboard_schema_instructions
            
            llm_with_structured_output = create_extractor(self.llm, tools=[dashboard_model])
        except NotImplementedError as exc:
            msg = f"{self.llm.__class__.__name__} does not support structured output."
            raise TypeError(msg) from exc
        
        config_dict = {
            "run_name": self.display_name,
            "project_name": self.get_project_name(),
            "callbacks": self.get_langchain_callbacks(),
        }
        
        result = get_chat_result(
            runnable=llm_with_structured_output,
            system_message=system_prompt,
            input_value=self.input_value,
            config=config_dict,
        )
        
        if isinstance(result, BaseModel):
            result = result.model_dump()
        if responses := result.get("responses"):
            result = responses[0].model_dump()
        if result and "dashboard" in result:
            return result["dashboard"]
            
        return result

    def build_structured_output(self) -> Data:
        """Return the structured output in a standard format."""
        output = self.build_structured_output_base()
        return Data(text_key="results", data={"results": output})

    def as_dataframe(self) -> DataFrame:
        """Convert the structured output to a DataFrame."""
        output = self.build_structured_output_base()
        if isinstance(output, list):
            return DataFrame(data=output)
        return DataFrame(data=[output])
    
    def get_visualization_data(self) -> Data:
        """Return the visualization data in a format that can be used by visualization components."""
        output = self.build_structured_output_base()
        
        # For Dashboard Visualization, return the visualization section directly
        if self.output_type == "Dashboard Visualization" and isinstance(output, dict):
            # If the output already has a 'visualization' key, return that
            if "visualization" in output:
                return Data(text_key="visualization", data={"visualization": output["visualization"]})
            # Otherwise return the whole output as the visualization data
            return Data(text_key="visualization", data={"visualization": output})
        
        # For Custom Schema, simply return the output
        return Data(text_key="visualization", data={"visualization": output})