from pydantic import BaseModel
from typing import Optional
class CheckAccountResponse(BaseModel):
    channel: Optional[str] = None
    idNum: Optional[str] = None
    idType: Optional[str] = None
    status: Optional[str] = None
    errorCode: Optional[str] = None
    errorMessage: Optional[str] = None