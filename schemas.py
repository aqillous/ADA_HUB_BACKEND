from pydantic import BaseModel
from datetime import date , time , datetime
from typing import List
from models import OrderStatus

class RegisterRequest(BaseModel):
    email:str
    password:str

class LoginRequest(BaseModel):
    email:str
    password:str

class AllUsersResponse(BaseModel):
    id:int
    email:str
    is_admin:bool

    class Config:
        from_attributes : True

class AddUserRequest(BaseModel):
    email:str
    password:str
    is_admin:bool

class CalendarEventRequest(BaseModel):
    event_date:date
    event_time:time
    event_name:str

class AllCalendarEventsResponse(BaseModel):
    id:int
    event_date:date
    event_time:time
    event_name:str

class AddNewsRequest(BaseModel):
    news_header: str
    news_short: str | None = None
    news_content: str

class AllNewsResponse(BaseModel):
    id: int
    news_header: str
    news_short: str | None = None
    news_content: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int

class OrderSchema(BaseModel):
    items: List[OrderItemSchema]

class ProductOut(BaseModel):
    id: int
    name: str
    price: int
    image_url: str | None = None

    class Config:
        from_attributes = True

class OrderItemOut(BaseModel):
    id: int
    quantity: int
    price: float
    subtotal: float
    product: ProductOut

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    name: str | None
    surname: str | None

    class Config:
        orm_mode = True


class OrderOut(BaseModel):
    id: int
    user: UserOut | None
    status: str
    total_amount: float
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class RefreshTokenRequest(BaseModel):
    refresh_token : str

class UpdateProfileRequest(BaseModel):
    name: str
    surname: str
    current_position: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str