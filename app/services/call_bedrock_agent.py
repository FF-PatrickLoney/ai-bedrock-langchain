import boto3
import uuid

from models.call_bedrock_agent_input_model import CallBedrockAgentInput


# https://docs.aws.amazon.com/code-library/latest/ug/python_3_bedrock-agent-runtime_code_examples.html
def prompt(call_bedrock_agent_input: CallBedrockAgentInput):
    print("Prompting...")

    bedrock_client = boto3.client(
        service_name="bedrock-agent-runtime",
        region_name="us-east-1",
    )

    input = call_bedrock_agent_input.input
    agent_id = call_bedrock_agent_input.agent_id
    agent_alias_id = call_bedrock_agent_input.agent_alias_id
    session_id = call_bedrock_agent_input.session_id

    print(f"Human: {input}")

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime/client/invoke_agent.html
    response_stream = bedrock_client.invoke_agent(
        inputText=input,
        endSession=False,
        enableTrace=False,
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=str(uuid.uuid4()) if session_id is None else session_id,
    )

    completion = ""

    for event in response_stream.get("completion"):
        chunk = event["chunk"]
        completion = completion + chunk["bytes"].decode()

    print(f"AI Assistant: {completion}")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": {
            "sessionId": response_stream["sessionId"],
            "text": completion
        },
    }
