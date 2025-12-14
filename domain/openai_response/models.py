from pydantic import BaseModel
from typing import List, Dict, Union, Optional

class OpenAIResponseAPI(BaseModel):
    model: str
    input: Union[List[Dict], str]
    instructions: Optional[str] = None
    stream: Optional[bool] = False
    tools: Optional[List[Dict]] = None