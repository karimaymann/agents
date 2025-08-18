import os
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain_core.prompts import PromptTemplate
from typing import Optional, Type
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(description="The location to get weather for")

class EmailInput(BaseModel):
    email: str = Field(description="Email address to send to")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body content")

class WeatherTool(BaseTool):
    name = "get_weather"
    description = "Get weather information for a location"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, location: str) -> str:
        # return weatherService.get_weather(location)
        return 

class EmailTool(BaseTool):
    name = "send_email"
    description = "Send an email to a user"
    args_schema: Type[BaseModel] = EmailInput
    
    def _run(self, email: str, subject: str, body: str) -> str:
        # return emailService.send_email(email, subject, body)
        return f"Sending email to {email} with subject '{subject}' and body '{body}'"

    

class DemoAgent:
    def __init__(self):
        self.tools = [WeatherTool(), EmailTool()]
        
        self.prompt = PromptTemplate(
            template="""
            You are a helpful assistant. Use the following tools to help users:

            1. WeatherTool: Get weather information for {location}.
            2. EmailTool: Send {name} an email about it.

            When asked a question, think about which tool would be best to use, and respond with the result of that tool.
            Use the provided location: {location} and name: {name} in your responses when relevant.
                       
            """,
            input_variables=["location", "name"]
        )
        
        self.llm = OpenAI(
            temperature=0, 
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        # Initialize agent with custom prompt
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            prompt=self.prompt,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )

    def run(self, location: str, name: str) -> str:
        """Run the agent with the given location and name"""
        try:
            formatted_input = self.prompt.format(
                location=location,
                name=name,
            )
            response = self.agent.run(formatted_input)
            return response
        except Exception as e:
            return f"Error running agent: {str(e)}"

# Example usage
def main():
    # Make sure to set your API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Initialize the demo agent
    demo_agent = DemoAgent()
    
    # Use the agent with location and name inputs
    location: str = "Barcelona"
    name: str = "John"
    
    query1 = "What's the weather like and can you email the person about it?"
    response1 = demo_agent.run(query1, location=location, name=name)
    print(f"Agent response 1: {response1}")
    
    # Another example
    query2 = "Get the weather information and send an email summary"
    response2 = demo_agent.run(query2, location=location, name=name)
    print(f"Agent response 2: {response2}")
    
    # Example with different inputs
    query3 = "How many users are in our database?"
    response3 = demo_agent.run(query3, location="Paris", name="Alice")
    print(f"Agent response 3: {response3}")

if __name__ == "__main__":
    main()