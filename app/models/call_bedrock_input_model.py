from pydantic import BaseModel
from typing import Optional

class CallBedrockInput(BaseModel):
    input: str
    session_id: Optional[str] = None

