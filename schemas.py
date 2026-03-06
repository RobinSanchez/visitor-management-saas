from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=72)
    institution_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class VisitorCreate(BaseModel):
    name: str
    email: EmailStr     

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    department: str      