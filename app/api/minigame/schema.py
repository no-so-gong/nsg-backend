from pydantic import BaseModel
from typing import Optional


class MinigameStartResponse(BaseModel):
    message: str
    data: dict
    status: int
