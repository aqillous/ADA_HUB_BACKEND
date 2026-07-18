from sqlalchemy import Column , Integer , String , Boolean , DateTime, Date , Time , Enum , Float , ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base
from datetime import datetime
import enum

class OrderStatus(str, enum.Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class PositionEnum(str, enum.Enum):
    igv_member = "iGV Member"
    igv_tl = "iGV Team Leader"
    ogv_member = "OGV Member"
    ogv_tl = "OGV Team Leader"
    lcvp = "LCVP"
    lcp = "LCP"
    alumnus = "Alumni"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String , nullable=False)
    hashed_password = Column(String , nullable=False)
    is_admin = Column(Boolean, default=False)

    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)

    current_position = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user")

class CalEvent(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    event_name = Column(String , nullable=False)
    event_date = Column(Date , nullable=False)
    event_time = Column(Time , nullable=False)
    created_at = Column(DateTime , default=datetime.utcnow)

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    news_header = Column(String , nullable=False)
    news_short = Column(String)
    news_content = Column(String)
    created_at = Column(DateTime , default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    hide = Column(Boolean , default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    total_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # snapshot of product price at order time
    subtotal = Column(Float, nullable=False)  # quantity * price

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class VP(Base):
    __tablename__ = "vps"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MaterialFolder(Base):
    __tablename__ = "material_folders"

    id = Column(Integer, primary_key=True, index=True)

    # NEW: self-referential parent for nested (Google-Drive-style) folders.
    # NULL parent_id => top-level ("root") folder.
    parent_id = Column(Integer, ForeignKey("material_folders.id"), nullable=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Role-based access (unchanged) — comma-separated PositionEnum values
    allowed_positions = Column(String, nullable=False, default="")

    # NEW: person-based access — comma-separated email addresses.
    # A user sees a (root) folder if EITHER their position OR their email matches.
    allowed_emails = Column(String, nullable=False, default="")

    # NEW: appearance
    color = Column(String, nullable=False, default="blue")   # key into FOLDER_COLORS on the frontend
    icon = Column(String, nullable=False, default="folder")  # key into FOLDER_ICONS on the frontend

    created_at = Column(DateTime, default=datetime.utcnow)

    files = relationship("MaterialFile", back_populates="folder", cascade="all, delete-orphan")

    # Self-referential nesting: folder.children / child.parent
    children = relationship(
        "MaterialFolder",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
        single_parent=True,
    )


class MaterialFile(Base):
    __tablename__ = "material_files"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("material_folders.id"))
    name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    # pdf, docx, google_doc, google_sheet, google_slide, google_drive, canva, link, ...
    file_type = Column(String, nullable=True)
    source = Column(String, nullable=False, default="upload")  # "upload" or "link"
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    folder = relationship("MaterialFolder", back_populates="files")
