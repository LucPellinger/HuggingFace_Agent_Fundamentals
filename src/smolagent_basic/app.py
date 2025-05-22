from smolagents import CodeAgent,DuckDuckGoSearchTool, HfApiModel,load_tool,tool, LiteLLMModel
import datetime
import requests
import pytz
import yaml
from tools.final_answer import FinalAnswerTool
from tools.visit_webpage import VisitWebpageTool 

import os

from Gradio_UI import GradioUI

# Below is an example of a tool that does nothing. Amaze us with your creativity !
@tool
def my_custom_tool(arg1:int, arg2:int)-> str: #it's import to specify the return type
    #Keep this format for the description / args / args description but feel free to modify the tool
    """A tool that summarizes two values.
    Args:
        arg1: the first argument
        arg2: the second argument
    """
    a = arg1 + arg2
    return f"the result is {a}"

@tool
def hello_world(country: str) -> str:
    """Greets the given country.
    Args:
        country: A string including the name of the given country. 
    """
    try:
        # Format date as YYYY-MM-DD (API only supports "today" or "random")
        #if isinstance(input_time, str):
        #    try:
        #        input_time = datetime.fromisoformat(input_time)
        #    except ValueError:
        #        return "Invalid datetime format. Please use ISO format: YYYY-MM-DDTHH:MM:SS"

        
        # API doesn't actually support querying by date, so we just show today's
        response = f"Hello to {country}, how are you?"
        return response
    except Exception as e:
        return f"Error occurred: {str(e)}"

@tool
def get_joke(result: str) -> str:
    """Fetches a joke from the Chuck Norris API.
    Args:
        result: A string including the date/time output string from get_current_time_in_timezone.
    """
    try:
        # Format date as YYYY-MM-DD (API only supports "today" or "random")
        #if isinstance(input_time, str):
        #    try:
        #        input_time = datetime.fromisoformat(input_time)
        #    except ValueError:
        #        return "Invalid datetime format. Please use ISO format: YYYY-MM-DDTHH:MM:SS"

        
        # API doesn't actually support querying by date, so we just show today's
        response = requests.get("https://api.chucknorris.io/jokes/random")
        if response.status_code == 200:
            data = response.json()
            return f"{result}. Here's a useless joke: {data.get('value', 'No joke found.')}"
        else:
            return f"Failed to fetch fact: {response.status_code}"
    except Exception as e:
        return f"Error occurred: {str(e)}"

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"


final_answer = FinalAnswerTool()

# If the agent does not answer, the model is overloaded, please use another model or the following Hugging Face Endpoint that also contains qwen2.5 coder:
# model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

# --- Configure LLM Model ---
if not os.getenv("GEMINI_TOKEN"):
    print("CRITICAL: GEMINI_TOKEN environment variable not set. LLM will not work.")
    # exit(1) # Or handle gracefully

model = LiteLLMModel(
    model_id="gemini/gemini-1.5-flash-latest",
    api_key=os.getenv("GEMINI_TOKEN"),
    max_tokens=4096,
    temperature=0.6
)

#model = HfApiModel(
#max_tokens=2096,
#temperature=0.5,
#model_id='Qwen/Qwen2.5-Coder-32B-Instruct',# it is possible that this model may be overloaded
#custom_role_conversions=None,
#)


# Import tool from Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)
internet_search_tool = DuckDuckGoSearchTool()
visit_webpage_tool = VisitWebpageTool()

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[
        final_answer,
        get_current_time_in_timezone, 
        image_generation_tool,
        visit_webpage_tool,
        internet_search_tool,
        hello_world, get_joke  # Include this!
    ], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()