import boto3
import json
import os

from langchain.llms.bedrock import Bedrock
from langchain.tools import Tool
from langchain_community.utilities import google_search
from langchain.agents import initialize_agent, agent_types

os.environ["GOOGLE_CSE_ID"] = os.getenv("GoogleSearchEngineId")
os.environ["GOOGLE_API_KEY"] = os.getenv("GoogleApiKey")

def execute_llm(bedrock_client, input):
        search = google_search.GoogleSearchAPIWrapper(k=5)

        tool = Tool(
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

        agent = initialize_agent(tools=[tool], llm=claude_llm,  agent=agent_types.AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

        response = agent.run(input)

        return response

def lambda_handler(event, context):
    print("Prompting...")
    bedrock = boto3.client(service_name='bedrock-runtime')

    body = json.loads(event['body'])
    input = body.get('input')

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
    }
