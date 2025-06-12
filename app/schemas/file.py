from pydantic import BaseModel
from datetime import datetime

class File(BaseModel):
    id: int
    name: str
    type: str
    size: int
    path: str
    modified: datetime

    class Config:
        from_attributes = True 