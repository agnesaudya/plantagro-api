from typing import Union
from pydantic import BaseModel

class InputData(BaseModel):
    province_name: str 
    municipality: Union[str, None] = None
    email: Union[str, None] = None
    type: Union[str, None] = None



class State(BaseModel):
    province_name: Union[str, None] = None
    municipality: Union[str, None] = None
    min_temp: Union[str, None] = None
    max_temp: Union[str, None] = None
    min_humid: Union[str, None] = None
    max_humid: Union[str, None] = None


    