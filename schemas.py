from pydantic import BaseModel
from datetime import date , time , datetime
from typing import List
from models import OrderStatus , PositionEnum

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    surname: str

class LoginRequest(BaseModel):
    email:str
    password:str

class AllUsersResponse(BaseModel):
    id: int
    email: str
    is_admin: bool
    name: str | None = None
    surname: str | None = None
    current_position: str | None = None   # was PositionEnum | None

    class Config:
        from_attributes = True

class UpdateUserPositionRequest(BaseModel):
    current_position: str

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
    price: float
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
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    user: UserOut | None
    status: OrderStatus
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

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class MaterialFolderCreate(BaseModel):
    name: str
    description: str | None = None
    allowed_positions: List[str]

class MaterialFileOut(BaseModel):
    id: int
    name: str
    file_url: str
    file_type: str | None = None
    uploaded_at: datetime

class MaterialFolderOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    allowed_positions: List[str]
    files: List[MaterialFileOut] = []

class MaterialLinkCreate(BaseModel):
    name: str
    url: str

class MaterialFileOut(BaseModel):
    id: int
    name: str
    file_url: str
    file_type: str | None = None
    source: str
    uploaded_at: datetime