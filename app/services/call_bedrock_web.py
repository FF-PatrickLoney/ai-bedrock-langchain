import boto3
import json
import os

from langchain.llms.bedrock import Bedrock
from langchain.tools import Tool
from langchain_community.utilities import google_search
from langchain.agents import initialize_agent, agent_types
from utils.secrets_manager_helper import get_secrets
from models.call_bedrock_input_model import CallBedrockInput
from config import Settings

def set_env_vars(settings: Settings): 
    secrets_dict = get_secrets(settings.environment)
    os.environ["GOOGLE_CSE_ID"] = secrets_dict.get("GoogleSearchEngineId")
    os.environ["GOOGLE_API_KEY"] = secrets_dict.get("GoogleApiKey")

def execute_llm(bedrock_client, input):
        search = google_search.GoogleSearchAPIWrapper(k=5)

        google_search_tool = Tool(
            name="Google Search",
            description="Search Google for recent results.",
            func=search.run,
        )

        inference_modifier = {
            'max_tokens_to_sample':1000, 
            "temperature":0.7,
            "top_k":250,
            "top_p":1,
            "stop_sequences": ["\n\nHuman"],
        }

        modelId = 'anthropic.claude-v2:1'
        
        claude_llm = Bedrock(
            model_id = modelId,
            client = bedrock_client,
            model_kwargs = inference_modifier,
        )

        tools = [google_search_tool]


        PREFIX = """Answer the following questions as best you can. You have access to the following tools:"""
        FORMAT_INSTRUCTIONS = """Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat a maximum of 5 times)
        ... Use this observation to provide your final answer.
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question"""
        SUFFIX = """Begin!

        Question: {input}
        Thought:{agent_scratchpad}"""

        agent = initialize_agent(
            tools=tools, 
            llm=claude_llm, 
            agent=agent_types.AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
            verbose=True, 
            #max_iterations=len(tools),
            handle_parsing_errors=True,     
            agent_kwargs={
                'prefix':PREFIX,
                'format_instructions':FORMAT_INSTRUCTIONS,
                'suffix':SUFFIX
            }
        )

        response = agent.invoke({"input": input})

        return response

def prompt(call_bedrock_input: CallBedrockInput, settings: Settings):
    set_env_vars(settings)
    print("Prompting...")
    bedrock = boto3.client(service_name='bedrock-runtime')

    input = call_bedrock_input.input

    print(f"Human: {input}")

    response = execute_llm(bedrock, input)

    print(f"AI Assistant: {response}")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": {
            "ai_response": json.dumps(response),
        },
        "isBase64Encoded": False
    }
