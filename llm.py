from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain.agents import Tool
from function import create_event, update_event, delete_event, get_upcoming_events
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from typing import Optional
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool

# Load environment variables
load_dotenv()

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models for input parameters
class DeleteEventParameters(BaseModel):
    event_name: str = Field(description="name of the event to be deleted")

class UpdateEventParameters(BaseModel):
    event_name: str = Field(description="name of the event to be updated")
    date: Optional[str] = Field(description="updated start date of the event (format: YYYY-MM-DD) (optional)")
    time: Optional[str] = Field(description="updated start time of the event (format: HH:MM) (optional)")
    duration: Optional[int] = Field(description="updated duration of the event in hours (optional)")
    name: Optional[str] = Field(description="updated name or title of the event (optional)")
    description: Optional[str] = Field(description="updated description or details of the event (optional)")
    location: Optional[str] = Field(description="updated location of the event (optional)")

class CreateEventParameters(BaseModel):
    date: str = Field(description="start date of the event (format: YYYY-MM-DD)")
    time: str = Field(description="start time of the event (format: HH:MM)")
    name: str = Field(description="name or title of the event")
    duration: int = Field(1, description="duration of the event in hours (default: 1)")
    description: Optional[str] = Field(None, description="description or details of the event (optional)")
    location: Optional[str] = Field(None, description="location of the event (optional)")

# query = input("Enter details: ")

def final_run(query):
    # Check if the chain was able to extract the parameters successfully
    if query and len(query) > 0:
        

        # Create a list of tools for the agent
        llm = OpenAI(temperature=0)
        tools = [
            StructuredTool.from_function(
                name="Create Event",
                func=create_event,
                description="Create an event in the Google calendar with the details provided",
                args_schema=CreateEventParameters
            ),
            StructuredTool.from_function(
                name="Update Event",
                func=update_event,
                description="Update an existing event in the Google calendar",
                args_schema=UpdateEventParameters
            ),
            StructuredTool.from_function(
                name="Delete Event",
                func=delete_event,
                description="Delete an event from the Google calendar",
                args_schema=DeleteEventParameters
            ),
        ]

        # Initialize the agent chain
        agent_chain = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
        response = agent_chain.run(input=query)
        print(response)
    else:
        print("Error: Unable to extract parameters from the user input.")
