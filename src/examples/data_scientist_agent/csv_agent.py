from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent

from langflow.base.agents.agent import LCAgentComponent
from langflow.field_typing import AgentExecutor
from langflow.inputs import DropdownInput, FileInput, HandleInput
from langflow.inputs.inputs import DictInput, MessageTextInput
from langflow.schema.message import Message
from langflow.template.field.base import Output


class CSVAgentComponent(LCAgentComponent):
    display_name = "CSVAgent"
    description = "Construct a CSV agent from a CSV and tools that outputs structured dashboard visualizations."
    documentation = "https://python.langchain.com/docs/modules/agents/toolkits/csv"
    name = "CSVAgent"
    icon = "LangChain"

    inputs = [
        *LCAgentComponent._base_inputs,
        HandleInput(
            name="llm",
            display_name="Language Model",
            input_types=["LanguageModel"],
            required=True,
            info="An LLM Model Object (It can be found in any LLM Component).",
        ),
        FileInput(
            name="path",
            display_name="File Path",
            file_types=["csv"],
            input_types=["str", "Message"],
            required=True,
            info="A CSV File or File Path.",
        ),
        DropdownInput(
            name="agent_type",
            display_name="Agent Type",
            advanced=True,
            options=["zero-shot-react-description", "openai-functions", "openai-tools"],
            value="openai-tools",
        ),
        MessageTextInput(
            name="input_value",
            display_name="Text",
            info="Text to be passed as input and extract info from the CSV File.",
            required=True,
        ),
        DictInput(
            name="pandas_kwargs",
            display_name="Pandas Kwargs",
            info="Pandas Kwargs to be passed to the agent.",
            advanced=True,
            is_list=True,
        ),
    ]

    outputs = [
        Output(display_name="Response", name="response", method="build_agent_response"),
        Output(display_name="Agent", name="agent", method="build_agent", hidden=True, tool_mode=False),
    ]

    def _path(self) -> str:
        if isinstance(self.path, Message) and isinstance(self.path.text, str):
            return self.path.text
        return self.path

    def _create_structured_prompt(self, user_query: str) -> str:
        # Create the prompt parts separately
        prompt_intro = f"User query: {user_query}\n\n"
        
        # Define the enhanced dashboard schema prompt instructions
        prompt_instructions = """
System Instructions:  
You are a data analysis AI specialized in creating interactive dashboards. Analyze the data in the CSV file, answer the user's query, and provide a comprehensive dashboard response.

Your response **MUST** follow this specific structure:

```json
{
  "response": {
    "answer": "Your direct answer to the user's question goes here.",
    "summary": "A brief summary of the key insights from the data analysis.",
    "additional_insights": [
      "Additional insight point 1 that might be helpful",
      "Additional insight point 2 that provides more context"
    ],
    "recommendations": [
      "Recommendation 1 based on the data",
      "Recommendation 2 for potential actions"
    ]
  },
  "visualization": {
    "has_plots": true,
    "display_mode": "dashboard",
    "dashboard": {
      "title": "Dashboard Title Based on the User's Query",
      "subtitle": "Optional subtitle with key metrics (e.g., Total Hours: 223.25)",
      "auto_layout": true,
      "plots": [
        {
          "id": "plot1",
          "title": "Primary Visualization Title",
          "description": "Describes what this visualization shows",
          "importance": 1,
          "plot_type": "bar|line|area|pie|scatter",
          "data": [
            {
              "x": ["Category A", "Category B", "Category C"],
              "y": [20, 35, 15],
              "type": "bar|line|area|pie|scatter",
              "orientation": "v|h",
              "mode": "lines+markers",
              "marker": {
                "color": "blue"
              }
            }
          ],
          "layout": {
            "height": 300,
            "margin": {"t": 30, "b": 40, "l": 60, "r": 20},
            "xaxis": {
              "title": "X-Axis Title"
            },
            "yaxis": {
              "title": "Y-Axis Title"
            }
          }
        }
      ]
    }
  },
  "metadata": {
    "total_records": 223,
    "time_period": "The time range covered by the data",
    "data_sources": ["report.csv"],
    "last_updated": "2025-05-20T10:30:00Z",
    "query_info": {
      "original_query": "The user's original question",
      "generated_plots": 1
    }
  }
}
```

Important Guidelines:

1. **RESPONSE SECTION**:
   - Provide a direct, concise answer to the user's question
   - Include a summary of key insights
   - List 2-3 additional insights not directly asked but relevant
   - Suggest 1-2 actionable recommendations based on the data

2. **VISUALIZATION DECISION**:
   - Carefully analyze the user's question to determine the appropriate number of plots:
     - **Simple Questions**: For straightforward queries like "How many hours did JSmith work?" or "What's the average time per task?", use a SINGLE plot that directly answers the question
     - **Comparative Questions**: For queries like "Compare hours worked by each employee" or "Show me time distribution by project", use 1-2 plots to highlight the comparison
     - **Complex Questions**: For multi-faceted questions like "Analyze our time tracking data" or "Give me a full breakdown of our project efficiency", create 3-4 plots that show different aspects of the data
   - **NEVER exceed 4 plots** in your response
   - Use the "importance" field to rank plots (1 = most important)
   - Update the "generated_plots" count in metadata to match the actual number of plots

3. **VISUALIZATION TYPES**:
   - Choose appropriate plot types for the data:
     - **Bar charts**: For comparisons across discrete categories (e.g., employees, projects)
     - **Line/area charts**: For time series or trends over time
     - **Pie charts**: For proportions or composition when there are fewer than 7 categories
     - **Scatter plots**: For relationship analysis between two variables
   - Ensure each plot has a clear title and axis labels
   - Set "has_plots" to false and "display_mode" to "none" if visualization isn't appropriate

4. **PLOT SPECIFICS**:
   - For time data, format dates consistently (e.g., "2023-01" for months)
   - For horizontal bar charts, set "orientation": "h" and swap x/y values
   - Use colors strategically (gradients for categories, consistent palette)
   - Ensure all required fields for each plot type are included
   - For multiple plots, make sure each has a unique "id" (plot1, plot2, etc.)

5. **METADATA**:
   - Include accurate record counts and date ranges from the data
   - List data sources used (file names)
   - Include the original user query
   - Specify how many plots were generated

Ensure your JSON is properly structured, with no syntax errors, and contains all required fields. The analysis should be data-driven and directly answer the user's question.
"""
        
        # Combine the parts
        return prompt_intro + prompt_instructions

    def build_agent_response(self) -> Message:
        agent_kwargs = {
            "verbose": self.verbose,
            "allow_dangerous_code": True,
        }

        agent_csv = create_csv_agent(
            llm=self.llm,
            path=self._path(),
            agent_type=self.agent_type,
            handle_parsing_errors=self.handle_parsing_errors,
            pandas_kwargs=self.pandas_kwargs,
            **agent_kwargs,
        )
        
        # Structure the prompt with the user's query
        structured_prompt = self._create_structured_prompt(self.input_value)
        
        # Pass the structured prompt to the agent
        result = agent_csv.invoke({"input": structured_prompt})
        
        # Process the result to extract the JSON if needed
        response_text = str(result["output"])
        
        # Attempt to find and clean JSON from the response if needed
        # This handles cases where the LLM might add extra text before or after the JSON
        import re
        import json
        
        # Try to extract JSON if it's embedded in text
        json_pattern = r'```json\s*([\s\S]*?)\s*```|^\s*(\{[\s\S]*\})\s*$'
        match = re.search(json_pattern, response_text)
        
        if match:
            # Get the matched JSON string (either from code block or raw)
            json_str = match.group(1) or match.group(2)
            
            try:
                # Parse the JSON to validate it
                parsed_json = json.loads(json_str.strip())
                # Return just the validated JSON as the response
                return Message(text=json.dumps(parsed_json, indent=2))
            except json.JSONDecodeError:
                # If JSON is invalid, return the original response
                pass
        
        return Message(text=response_text)

    def build_agent(self) -> AgentExecutor:
        agent_kwargs = {
            "verbose": self.verbose,
            "allow_dangerous_code": True,
        }

        agent_csv = create_csv_agent(
            llm=self.llm,
            path=self._path(),
            agent_type=self.agent_type,
            handle_parsing_errors=self.handle_parsing_errors,
            pandas_kwargs=self.pandas_kwargs,
            **agent_kwargs,
        )

        self.status = Message(text=str(agent_csv))

        return agent_csv