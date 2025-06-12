from pydantic import BaseModel
from typing import Dict, Any, Optional

class StorageBase(BaseModel):
    name: str
    type: str
    config: str

class StorageCreate(StorageBase):
    pass

class StorageUpdate(StorageBase):
    pass

class Storage(StorageBase):
    id: int

    class Config:
        from_attributes = True 