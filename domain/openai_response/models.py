from pydantic import BaseModel
from typing import List, Dict, Union, Optional, Any

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
    model: str
    input: Union[List[Dict], str]
    instructions: Optional[str] = None
    stream: Optional[bool] = True
    tools: Optional[List[OpenAIToolsModel]] = None