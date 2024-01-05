import boto3
import json
import os
import logging

from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.llms.bedrock import Bedrock
from langchain.retrievers import AmazonKnowledgeBasesRetriever

import logging
log = logging.getLogger()
log.setLevel("INFO")

# import requests

def execute_llm(bedrock_client, input, session_id):
        # inference_modifier = {
        #     'max_tokens_to_sample':4096, 
        #     "temperature":0.5,
        #     "top_k":250,
        #     "top_p":1,
        #     "stop_sequences": ["\n\nHuman"],
        #     "sessionId": "session_id"
        # }
        
        # claude_llm = Bedrock(
        #     model_id = "anthropic.claude-v2",
        #     client = bedrock_client,
        #     model_kwargs = inference_modifier,
        # )

        # #TODO: Change for local DB copy of Nexus (or other app, for testing)
        # db = SQLDatabase.from_uri("mysql+pymysql://patrick:local.db.pass9876@127.0.0.1/employees") 
        # db_chain = SQLDatabaseChain.from_llm(llm=claude_llm, db=db, verbose=True)
        # db_chain.use_query_checker()

        # response = db_chain.run("How many employees are there?")

        # retriever = AmazonKnowledgeBasesRetriever(
        #     knowledge_base_id="PUIJP4EQUA",
        #     retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}, },

        # )
        body = json.dumps({
            "prompt": f"\n\nHuman:{input}\n\nAssistant:",
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 250,
            "max_tokens_to_sample": 1000,
            "stop_sequences": ["\n\nHuman:"]
        })
        modelId = 'anthropic.claude-v2:1'
        accept = 'application/json'
        contentType = 'application/json'

        response = bedrock_client.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

        # response = bedrock_client.retrieve_and_generate(
        #     sessionId=session_id,
        #     input={
        #         'text': input
        #     },
        #     retrieveAndGenerateConfiguration={
        #         'type': 'KNOWLEDGE_BASE',
        #         'knowledgeBaseConfiguration': {
        #             'knowledgeBaseId': os.environ['KNOWLEDGE_BASE_ID'],
        #             'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2'
        #         }
        #     }
        # )
        return response

def lambda_handler(event, context):
    print("Prompting...")
    bedrock = boto3.client(service_name='bedrock-runtime')

    body = json.loads(event['body'])
    input = body.get('input')
    session_id = body.get("sessionId")

    print(f"Human: {input}")

    response = execute_llm(bedrock, input, session_id)
    response_body = json.loads(response.get('body').read())
    completion = response_body.get('completion')

    print(f"AI Assistant: {completion}")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": {
            "ai_response": json.dumps(response_body),
            # "sessionId": response["sessionId"],
            # "citations": response["citations"]
        },
    }
