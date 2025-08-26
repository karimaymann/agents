import json
import os
import gradio as gr
from openai import OpenAI
import psycopg2
import requests

from dotenv import load_dotenv


load_dotenv(override=True)

def push(message):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": message
        }
    )

def record_user_details(email, name, notes="not provided"):
    push(f"{name} with email {email} would like to get in touch. Notes: {notes}")
    return {"recorded user details": "ok"}

def record_unknown_question(question):
    push(f"Recording unknown question: {question}")
    return {"pushed unknown question notification": "ok"}

record_user_details_json = {
    "name": "record_user_details",  
    "description": "Use this tool to record that a user is interested in getting in touch and provided an email address",
    "parameters":{
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of the user"
            },
            "name":{
                "type": "string",
                "description": "The name of the user"
            },
            "notes":{
                "type":"string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required" : ["email" ,"name"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Use this tool to record a question that you do not know the answer to",
    "parameters":{
        "type":"object",
        "properties":{
            "question":{
                "type":"string",
                "description":"The question the user asked"
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }
}


tools = [{"type": "function", "function": record_user_details_json},
         {"type":"function", "function": record_unknown_question_json}]

class CareerBot:
    def __init__(self):
        self.name = "Karim Ayman"
        self.model = OpenAI(api_key= os.getenv("GOOGLE_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        with open("me/KarimAymanElsaeed.tex", "r", encoding="utf-8") as f:
            self.resume = f.read()
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()   

    def handle_tool_call(self, tool_calls):
        results = []
        for call in tool_calls:
            tool_name = call.function.name
            arguments = json.loads(call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": call.id})
        return results  
    
    def get_system_prompt(self):
        system_prompt = f"""
        You are acting as {self.name}, answering questions on his behalf, particularly questions related to his career, professional experience,
        and skills. 
        Your responsibility is to represent {self.name} for interactions as faithfully as possible.
        You have access to a lot of information about {self.name}'s career and background, you are given a summary of his professional experience, skills, and interests, alongside
        his resume, which you can use to answer questions.
        Be professional and engaging, as if talking to a potential client or future employer who came across the website.
        Record every question and generated response into my local database using the record_user_interaction tool.
        If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career.
        If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and name, and record it using the record_user_details_tool.
        """

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## Resume:\n{self.resume}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role":"system", "content": self.get_system_prompt()}] + history + [{"role":"user", "content": message}]
        done = False
        while not done:
            response = self.model.chat.completions.create(model="gemini-2.0-flash", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                calls = message.tool_calls
                results = self.handle_tool_call(calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    bot = CareerBot()

    gr.ChatInterface(
        fn=bot.chat,
        type="messages",
        title="Karim Ayman Elsaeed",
        description="Ask me anything about my career, experience, or skill acquisition.",
        theme="default",  
        chatbot=gr.Chatbot(
            type="messages", 
            height=500,
            show_label=False
        ),
        textbox=gr.Textbox(
            placeholder="Type your question here...",
            container=True,
            scale=7,
        ),
        examples=[
            ["Talk about your professional experience."],
            ["What are your main technical skills?"],
            ["What are your personal interests?"]
        ],
        cache_examples=False,
    ).launch()






