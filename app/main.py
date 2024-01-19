import boto3
import json
import os
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, RedirectResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Annotated
from functools import lru_cache

import config
from models.call_bedrock_input_model import CallBedrockInput
from models.call_bedrock_agent_input_model import CallBedrockAgentInput
from services import call_bedrock_kb, call_bedrock_agent, call_bedrock_sql, call_bedrock_web, agent_action_group_1

app = FastAPI()

app.mount("/demo", StaticFiles(directory="static", html=True))

@lru_cache
def get_settings():
    return config.Settings()

@app.get("/")
async def root():
    return RedirectResponse(url='/demo/')

class Story(BaseModel):
   topic: Optional[str] = None

bedrock = boto3.client('bedrock-runtime')

async def bedrock_stream(topic: str):
    instruction = f"""
    You are a world class writer. Please write a sweet bedtime story about {topic}.
    """
    
    body = json.dumps({
        'prompt': f'Human:{instruction}\n\nAssistant:', 
        'max_tokens_to_sample': 1028,
        'temperature': 1,
        'top_k': 250,
        'top_p': 0.999,
        'stop_sequences': ['\n\nHuman:']
    })
    response = bedrock.invoke_model_with_response_stream(
        modelId='anthropic.claude-v2',
        body=body
    )

    stream = response.get('body')
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                yield json.loads(chunk.get('bytes').decode())['completion']

@app.post("/api/story")
def api_story(story: Story):
    if story.topic == None or story.topic == "":
       return None

    return StreamingResponse(bedrock_stream(story.topic), media_type="text/html")

# Bedrock Endpoints
@app.post("/api/call-bedrock-kb")
def call_bedrock_kb_endpoint(bedrock_input: CallBedrockInput, settings: Annotated[config.Settings, Depends(get_settings)]):
   return call_bedrock_kb.prompt(bedrock_input, settings)

@app.post("/api/call-bedrock-agent")
def call_bedrock_agent_endpoint(bedrock_agent_input: CallBedrockAgentInput):
   return call_bedrock_agent.prompt(bedrock_agent_input)

@app.post("/api/call-bedrock-web")
def call_bedrock_web_endpoint(bedrock_input: CallBedrockInput, settings: Annotated[config.Settings, Depends(get_settings)]):
   return call_bedrock_web.prompt(bedrock_input, settings)

@app.post("/api/call-bedrock-sql")
def call_bedrock_sql_endpoint(bedrock_input: CallBedrockInput, settings: Annotated[config.Settings, Depends(get_settings)]):
   return call_bedrock_sql.prompt(bedrock_input, settings)


# Agent Action Group Endpoints
@app.get("/api/agents/reports")
def get_reports():
   return agent_action_group_1.retrieve_reports()


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
