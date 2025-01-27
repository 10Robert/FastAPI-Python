from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Union



class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str
    user_id: int

class PartialUpdateUserRequest(BaseModel):
    username: Optional[str] | None = None
    email: Optional[str] | None = None
    first_name: Optional[str] | None = None
    last_name: Optional[str] | None = None
    role: Optional[str] | None = None
    phone_number: Optional[str] | None = None
    password: Optional[str] | None = None

class Token(BaseModel):
    access_token: str
    token_type: str


class UserVerification(BaseModel):
     password: str 
     new_password: str  = Field(min_length=6)

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool 

UserType = Dict[str, Union[int, str]]
userListType = List[UserType]

UpdateUserValuesType = Dict[str, Union[int, str]]