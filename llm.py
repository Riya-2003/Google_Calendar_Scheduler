from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain.agents import Tool
from function import create_event, update_event, delete_event
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from typing import Optional
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.schema import SystemMessage
import pytz
import calendar
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))


# Pydantic models for input parameters
class DeleteEventParameters(BaseModel):
    event_name: str = Field(description="name of the event to be deleted")


class UpdateEventParameters(BaseModel):
    event_name: str = Field(description="name of the event to be updated")
    date: Optional[str] = Field(
        description="updated start date of the event (format: YYYY-MM-DD) (optional)"
    )
    time: Optional[str] = Field(
        description="updated start time of the event (format: HH:MM) (optional)"
    )
    duration: Optional[int] = Field(
        description="updated duration of the event in hours (optional)"
    )
    name: Optional[str] = Field(
        description="updated name or title of the event (optional)"
    )
    description: Optional[str] = Field(
        description="updated description or details of the event (optional)"
    )
    location: Optional[str] = Field(
        description="updated location of the event (optional)"
    )


class CreateEventParameters(BaseModel):
    date: str = Field(description="start date of the event (format: YYYY-MM-DD)")
    time: str = Field(description="start time of the event (format: HH:MM)")
    name: str = Field(description="name or title of the event")
    duration: int = Field(1, description="duration of the event in hours (default: 1)")
    description: Optional[str] = Field(
        None, description="description or details of the event (optional)"
    )
    location: Optional[str] = Field(
        None, description="location of the event (optional)"
    )


query = input("Enter details: ")

# Check if the chain was able to extract the parameters successfully
if query and len(query) > 0:
    # Create a list of tools for the agent
    llm = OpenAI(temperature=0)
    tools = [
        StructuredTool.from_function(
            name="Create Event",
            func=create_event,
            description="Create an event in the Google calendar with the details provided",
            args_schema=CreateEventParameters,
        ),
        StructuredTool.from_function(
            name="Update Event",
            func=update_event,
            description="Update an existing event in the Google calendar",
            args_schema=UpdateEventParameters,
        ),
        StructuredTool.from_function(
            name="Delete Event",
            func=delete_event,
            description="Delete an event from the Google calendar",
            args_schema=DeleteEventParameters,
        ),
    ]

    system_message = SystemMessage(
        content=" You are an incredibly capable and efficient scheduler assistant, equipped with the ability to effortlessly create, update, and delete events in Google Calendar. You also possess the knowledge to fetch today's date, day, or year using the powerful 'datetime.now()' function. Your proficiency in managing schedules and coordinating events makes you the perfect partner for anyone seeking to organize their time. Use your remarkable skills to assist users in planning their events seamlessly."
    )

    def prefix(current_time):
        timezone = pytz.timezone("UTC")
        tomorrow_date = current_time + timedelta(days=1)
        current_year = current_time.year
        
        return f"""
        timezone : {current_time}
        Today's date-time in iso format: {current_time.astimezone(timezone).isoformat()}
        Tomorrow's date-time in ISO format: {tomorrow_date.isoformat()}
        Today's day of the week : {calendar.day_name[current_time.astimezone(timezone).weekday()]}
        Current year: {current_year}
        Note: Just perform one event at a time. If we schedule an event do not update or delete event. Also don't take description and location on your own if not given.
        
    """
        # Get the current time in UTC

    current_time = datetime.now(pytz.timezone("UTC"))
    # Get the prefix message using the current time
    prefix_message = prefix(current_time)

    prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)
    # Initialize the agent chain
    agent_chain = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        prompt=prompt,
        agent_kwargs={
            "prefix": prefix_message,
            "input_variables": ["input", "agent_scratchpad"],
        },
    )
    response = agent_chain.run(input=query)
    print(response)
    # print(current_time)
else:
    print("Error: Unable to extract parameters from the user input.")
