import boto3
import json
import os

from langchain.prompts import ChatPromptTemplate
from langchain.sql_database import SQLDatabase
from langchain.llms.bedrock import Bedrock
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from secrets_manager_helper import get_secrets


def execute_llm(bedrock_client, input):
        secrets_dict = get_secrets(os.environ['Environment'])

        db = SQLDatabase.from_uri(secrets_dict.get('DatabaseUri'))

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
        parsed_sql_query = sql_query[index1 + len(sql_delimiter_1) + 1: index2 + 1].strip()

        print("***** SQL QUERY ****")
        print(parsed_sql_query)
        print("********************")

        full_template = """
        You are a MySQL expert.
        Based on the table schema below, question, sql query, and sql response:
        Table Schema: {schema}
        Question: {question}
        SQL Query: {query}
        SQL Response: {response}
        
        Use the following format for your response:

        Question: Question here
        SQLQuery: SQL Query to run
        SQLResult: Result of the SQLQuery
        Answer: Final answer in natural language here
        """
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
