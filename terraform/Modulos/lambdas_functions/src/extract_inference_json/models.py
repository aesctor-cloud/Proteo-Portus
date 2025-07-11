from pydantic import BaseModel
from typing import List, Union

class Filter(BaseModel):
    field: str
    operator: str
    value: Union[str, int, float]

class FilterResult(BaseModel):
    filters: List[Filter]
    embedding_fields: str