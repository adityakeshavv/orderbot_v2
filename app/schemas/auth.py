from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    name:     str
    email:    EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class UserOut(BaseModel):
    id:    int
    name:  str
    email: str
    role:  str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserOut
