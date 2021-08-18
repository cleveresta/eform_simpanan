from pydantic import BaseModel
class CheckAccountRequest(BaseModel):
    channel: str
    idNum: str
    idType: str
    pob: str
    dateOfBirth: str