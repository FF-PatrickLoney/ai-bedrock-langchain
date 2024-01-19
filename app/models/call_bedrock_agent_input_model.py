from models.call_bedrock_input_model import CallBedrockInput

class CallBedrockAgentInput(CallBedrockInput):
    agent_id: str
    agent_alias_id: str

