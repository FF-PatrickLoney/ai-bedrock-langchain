import boto3
import json
import os

from utils.secrets_manager_helper import get_secrets
from models.call_bedrock_input_model import CallBedrockInput
from config import Settings


def execute_llm(bedrock_client, input, session_id):
    response = ""
    if (session_id is None):
        response = bedrock_client.retrieve_and_generate(
            input={
                'text': input
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': os.environ['KnowledgeBaseId'],
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2'
                }
            }
        )
    else:
        response = bedrock_client.retrieve_and_generate(
        sessionId=session_id,
        input={
            'text': input
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': os.environ['KnowledgeBaseId'],
                'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2'
            }
        }
    )
    return response

def prompt(call_bedrock_input: CallBedrockInput, settings: Settings):
    print("Prompting...")
    secrets_dict = get_secrets(settings.environment)
    os.environ['KnowledgeBaseId'] = secrets_dict.get('KnowledgeBaseId')
    
    bedrock_client = boto3.client(
        service_name="bedrock-agent-runtime",
        region_name="us-east-1",
    )

    input = call_bedrock_input.input
    session_id = call_bedrock_input.session_id

    print(f"Human: {input}")

    response = execute_llm(bedrock_client, input, session_id)

    print(f"AI Assistant: {response}")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": {
            "text": json.dumps(response["output"]["text"]),
            "sessionId": response["sessionId"],
            "citations": response["citations"]
        },
        "isBase64Encoded": False
    }