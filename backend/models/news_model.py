from pydantic import BaseModel
from typing import Optional


class NewsResponse(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    sentiment: Optional[str] = None
    published: Optional[str] = None
    link: Optional[str] = None