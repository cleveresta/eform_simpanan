from pydantic import BaseModel
from typing import Optional
class CreateAccountResponse(BaseModel):
    refNum : str
    channel: Optional[str] = None
    cifNum : Optional[str] = None
    accountNum: Optional[str] = None
    newAccountNum: Optional[str] = None
    customerName: Optional[str] = None
    idNum: Optional[str] = None
    idType: Optional[str] = None
    status: Optional[str] = None
    errorCode: Optional[str] = None
    errorMessage: Optional[str] = None