from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Any
from domain.openai_response.prompt import system_prompt

class OpenAIToolsParametersModel(BaseModel):
    type: str
    propertires: Dict[str, Any]
    required: Optional[List[str]] = None

class OpenAIToolsModel(BaseModel):
    type: str
    name: str
    description: Optional[str] = None
    parameters: Optional[OpenAIToolsParametersModel] = None

class OpenAIResponseAPIModel(BaseModel):
    session_id: Optional[int] = None
    model: str
    input: Union[List[Dict], str]
    instructions: Optional[str] = system_prompt
    stream: Optional[bool] = False
    tools: Optional[List[OpenAIToolsModel]] = None