from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 