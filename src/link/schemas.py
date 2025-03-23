from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class link(BaseModel):
    id: Optional[int] = Field(default=None)
    login_user: Optional[str] = None
    full_link : str
    short_link: str
    expiration_date : Optional[datetime] = None
    is_deleted: bool