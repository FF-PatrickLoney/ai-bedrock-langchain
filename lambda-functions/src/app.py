import boto3
import json
import os
import logging

from langchain.prompts import ChatPromptTemplate
from langchain.sql_database import SQLDatabase
from langchain.llms.bedrock import Bedrock
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


import logging
log = logging.getLogger()
log.setLevel("INFO")

def execute_llm(bedrock_client, input, session_id):
        db = SQLDatabase.from_uri("your-mysql-uri-here")

        def get_schema(_):
            return db.get_table_info()
        
        query_template = """Based on the table schema below, write a SQL query that would answer the user's question:
        {schema}

        Question: {question}
        SQL Query:"""
        prompt = ChatPromptTemplate.from_template(query_template)


        inference_modifier = {
            'max_tokens_to_sample':1000, 
            "temperature":0.7,
            "top_k":250,
            "top_p":1,
            "stop_sequences": ["\n\nHuman"],
        }

        modelId = 'anthropic.claude-v2:1'
        accept = 'application/json'
        contentType = 'application/json'
        
        claude_llm = Bedrock(
            model_id = modelId,
            client = bedrock_client,
            model_kwargs = inference_modifier,
        )

        sql_response = (
            RunnablePassthrough.assign(schema=get_schema)
            | prompt
            | claude_llm.bind(stop=["\nSQLResult:"])
            | StrOutputParser()
        )

        sql_query = sql_response.invoke({"question": input})
        sql_delimiter_1 = "sql"
        sql_delimiter_2 = ";"
        index1 = sql_query.find(sql_delimiter_1)
        index2 = sql_query.find(sql_delimiter_2)
        parsed_sql_query = sql_query[index1 + len(sql_delimiter_1) + 1: index2].strip()

        print("***** SQL QUERY ****")
        print(parsed_sql_query)
        print("***********************")

        full_template = """Based on the table schema below, question, sql query, and sql response, write a natural language response:
        {schema}

        Question: {question}
        SQL Query: {query}
        SQL Response: {response}"""
        prompt_response = ChatPromptTemplate.from_template(full_template)

        full_chain = (
            RunnablePassthrough.assign(query=sql_response).assign(
                schema=get_schema,
                response=lambda x: db.run(parsed_sql_query),
            )
            | prompt_response
            | claude_llm
        )

        response = full_chain.invoke({"question": input})



        # body = json.dumps({
        #     "prompt": f"\n\nHuman:{input}\n\nAssistant:",
        #     "temperature": 0.7,
        #     "top_p": 1,
        #     "top_k": 250,
        #     "max_tokens_to_sample": 1000,
        #     "stop_sequences": ["\n\nHuman:"]
        # })

        # response = bedrock_client.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

        return response

def lambda_handler(event, context):
    print("Prompting...")
    bedrock = boto3.client(service_name='bedrock-runtime')

    body = json.loads(event['body'])
    input = body.get('input')
    session_id = body.get("sessionId")

    print(f"Human: {input}")

    response = execute_llm(bedrock, input, session_id)
    # response_body = json.loads(response.get('body').read())
    # completion = response_body.get('completion')

    print(f"AI Assistant: {response}")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": {
            "ai_response": json.dumps(response),
            # "sessionId": response["sessionId"],
            # "citations": response["citations"]
        },
    }
