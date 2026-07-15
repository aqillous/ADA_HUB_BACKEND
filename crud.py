# --- crud.py ---
from sqlalchemy.orm import Session , joinedload
from sqlalchemy import func
from models import *
from authentication import  *
from datetime import date , time , timedelta , datetime
from fastapi import HTTPException

def register_user(
    db: Session,
    email: str,
    password: str,
    is_admin: bool = False,
    name: str = "",
    surname: str = ""
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return {"status": "error", "message": "existing user"}

    hashed_pw = hash_password(password)
    new_user = User(
        email=email,
        hashed_password=hashed_pw,
        is_admin=is_admin,
        name=name,
        surname=surname
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "user": {"id": new_user.id, "email": new_user.email, "is_admin": new_user.is_admin}}

def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"status": "error", "message": "user doesn't exist"}
    if not verify_password(password, user.hashed_password):
        return {"status": "error", "message": "wrong password"}

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "is_admin": user.is_admin,
    })
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "status": "success",
        "token": token,
        "refresh_token": refresh_token,
        "user": {"id": user.id, "email": user.email, "is_admin": user.is_admin}
    }

def all_users(db: Session):
    return db.query(User).all()

def delete_user(db:Session, user_id:int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"status": "error", "message": "user doesn't exist"}

    db.delete(user)
    db.commit()
    return {"status": "success"}

def edit_user(db:Session , user_id: int , is_admin:bool):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return {"status": "error", "message": "user doesn't exist"}

    user.is_admin = is_admin
    db.commit()
    db.refresh(user)

def add_calendar_event(db:Session , event_date:date , event_time:time , event_name:str):

    new_event = CalEvent(event_date=event_date , event_time=event_time , event_name = event_name)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return {"status": "success", "event": {"id": new_event.id, "event_date": new_event.event_date, "event_time": new_event.event_time , "event_name": new_event.event_name}}

def all_calendar_events(db:Session):
    return db.query(CalEvent).all()

def delete_calendar_event(db: Session , id:int):
    cal_event = db.query(CalEvent).filter(CalEvent.id == id).first()

    if not cal_event:
        return {"status": "error", "message": "event doesn't exist"}
    
    db.delete(cal_event)
    db.commit()

def edit_calendar_event(db:Session , id:int , event_name:str , event_date:date , event_time:time):
    cal_event = db.query(CalEvent).filter(CalEvent.id == id).first()
    
    if not cal_event:
        return {"status": "error", "message": "event doesn't exist"}
    
    cal_event.event_name = event_name
    cal_event.event_date= event_date
    cal_event.event_time = event_time
    db.commit()
    db.refresh(cal_event)

def add_news(db:Session , news_header:str , news_content:str , news_short:str= ""):
    new_news = News(news_header = news_header , news_content = news_content , news_short=news_short)
    db.add(new_news)
    db.commit()
    db.refresh(new_news)
    return {
    "status": "success",
    "news": {
        "id": new_news.id,
        "news_header": new_news.news_header,
        "news_short": new_news.news_short,
        "news_content": new_news.news_content,
        "created_at": new_news.created_at
        }
    }   
    
def all_news(db:Session):
    return db.query(News).all()

def delete_news(db:Session , id:int):
    existing_news = db.query(News).filter(News.id == id).first()

    if not existing_news:
        return {"status": "error", "message": "news doesn't exist"}
    
    db.delete(existing_news)
    db.commit()

def edit_news(db:Session , id:int , news_header:str , news_content:str):
        
    existing_news = db.query(News).filter(News.id == id).first()

    if not existing_news:
        return {"status": "error", "message": "news doesn't exist"}
    
    existing_news.news_header = news_header
    existing_news.news_content = news_content

    db.commit()
    db.refresh(existing_news)

def add_product(db:Session , name:str , price:float , image_url:str , is_hide:bool = False ):
    new_product = Product(name=name , price=price , image_url=image_url , hide=is_hide)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"status": "success", "product": {"id": new_product.id, "news_header": new_product.name}}

def get_all_products(db: Session, include_hidden=False):
    query = db.query(Product)
    if not include_hidden:
        query = query.filter(Product.hide == False)
    return query.all()

def hide_product(db: Session, product_id: int, hide: bool = True):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.hide = hide
        db.commit()
        db.refresh(product)
    return product

def edit_product(db: Session, product_id: int, name: str, price: float, image_url: str = None):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"status": "error", "message": "product doesn't exist"}

    product.name = name
    product.price = price
    if image_url:
        product.image_url = image_url

    db.commit()
    db.refresh(product)
    return {"status": "success", "product": {"id": product.id, "name": product.name, "price": product.price, "image_url": product.image_url}}

def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"status": "error", "message": "product doesn't exist"}

    db.delete(product)
    db.commit()
    return {"status": "success"}

def get_product(db:Session , product_id:int):
    return db.query(Product).filter(Product.id == product_id).first()
    
def create_order(db: Session, user_id: int, order_data):
    # create main order
    order = Order(user_id=user_id)
    db.add(order)
    db.commit()
    db.refresh(order)

    total = 0
    # iterate over order items properly
    for item in order_data.items:  # ✅ use .items because it's Pydantic
        product_id = item.product_id
        quantity = item.quantity

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            continue  # or raise HTTPException

        subtotal = product.price * quantity
        total += subtotal

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            price=product.price,
            subtotal=subtotal
        )
        db.add(order_item)

    order.total_amount = total
    db.commit()
    db.refresh(order)
    return order


def get_all_orders(db: Session):
    return db.query(Order).options(
        joinedload(Order.user) ,joinedload(Order.items).joinedload(OrderItem.product)
    ).all()

def change_order_status(db:Session , order_id , new_status):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"status": "error", "message": "order doesn't exist"}

    order.status= new_status
    db.commit()
    db.refresh(order)
    return {"status": "success", "order": {"id": order.id}}

def delete_order(db:Session , order_id):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"status": "error", "message": "order doesn't exist"}

    db.delete(order)
    db.commit()
    return {"status": "success"}




def get_dashboard_stats(db: Session):
    # ===== BASIC STATS =====
    total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
    total_orders = db.query(func.count(Order.id)).scalar() or 0

    avg_order = total_revenue / total_orders if total_orders else 0

    # Orders today
    today_start = datetime.combine(datetime.today(), datetime.min.time())
    today_orders = db.query(func.count(Order.id)).filter(
        Order.created_at >= today_start
    ).scalar() or 0

    # ===== REVENUE CHART (last 7 days) =====
    last_7_days = datetime.today() - timedelta(days=7)

    revenue_data = (
        db.query(
            func.date(Order.created_at).label("date"),
            func.sum(Order.total_amount).label("revenue")
        )
        .filter(Order.created_at >= last_7_days)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    revenue_chart = [
        {
            "date": str(r.date),
            "revenue": float(r.revenue or 0)
        }
        for r in revenue_data
    ]

    # ===== ORDERS CHART =====
    orders_data = (
        db.query(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("orders")
        )
        .filter(Order.created_at >= last_7_days)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    orders_chart = [
        {
            "date": str(o.date),
            "orders": o.orders
        }
        for o in orders_data
    ]

    # ===== TOP PRODUCTS =====
    top_products = (
        db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label("sold")
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    top_products_data = [
        {
            "id": p.id,
            "name": p.name,
            "sold": int(p.sold or 0)
        }
        for p in top_products
    ]

    # ===== RECENT ORDERS =====
    recent_orders = (
        db.query(Order)
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )

    recent_orders_data = [
        {
            "id": o.id,
            "total": float(o.total_amount or 0)
        }
        for o in recent_orders
    ]

    # ===== FINAL RESPONSE =====
    return {
        "totalRevenue": float(total_revenue),
        "totalOrders": total_orders,
        "avgOrder": round(avg_order, 2),
        "ordersToday": today_orders,

        "revenueChart": revenue_chart,
        "ordersChart": orders_chart,

        "topProducts": top_products_data,
        "recentOrders": recent_orders_data
    }

def get_me(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    return {
        "email": user.email,
        "name": user.name or "",
        "surname": user.surname or "",
        "current_position": user.current_position or "",   # plain string now, no .value
        "is_admin": user.is_admin,
    }

def update_profile(db: Session, user_id: int, name: str, surname: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"status": "error", "message": "user not found"}
    user.name = name
    user.surname = surname
    db.commit()
    db.refresh(user)
    return {"status": "success"}


def update_user_position(db: Session, user_id: int, position: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"status": "error", "message": "user not found"}
    user.current_position = position
    db.commit()
    db.refresh(user)
    return {"status": "success", "current_position": user.current_position}

def change_password(db: Session, user_id: int, current_password: str, new_password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"status": "error", "message": "User not found"}
    if not verify_password(current_password, user.hashed_password):
        return {"status": "error", "message": "Current password is incorrect"}
    user.hashed_password = hash_password(new_password)
    db.commit()
    return {"status": "success"}

def get_user_orders(db: Session, user_id: int):
    return (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_all_vps(db: Session):
    return db.query(VP).order_by(VP.created_at.asc()).all()

def add_vp(db: Session, name: str, position: str, image_url: str = None):
    vp = VP(name=name, position=position, image_url=image_url)
    db.add(vp)
    db.commit()
    db.refresh(vp)
    return {"status": "success", "vp": {"id": vp.id, "name": vp.name, "position": vp.position, "image_url": vp.image_url}}

def edit_vp(db: Session, vp_id: int, name: str, position: str, image_url: str = None):
    vp = db.query(VP).filter(VP.id == vp_id).first()
    if not vp:
        return {"status": "error", "message": "VP not found"}
    vp.name = name
    vp.position = position
    if image_url:
        vp.image_url = image_url
    db.commit()
    db.refresh(vp)
    return {"status": "success", "vp": {"id": vp.id, "name": vp.name, "position": vp.position, "image_url": vp.image_url}}

def delete_vp(db: Session, vp_id: int):
    vp = db.query(VP).filter(VP.id == vp_id).first()
    if not vp:
        return {"status": "error", "message": "VP not found"}
    db.delete(vp)
    db.commit()
    return {"status": "success"}

def folder_to_dict(f):
    positions = [p.strip() for p in (f.allowed_positions or "").split(",") if p.strip()]
    return {
        "id": f.id,
        "name": f.name,
        "description": f.description,
        "allowed_positions": positions,
        "files": [
            {
                "id": file.id,
                "name": file.name,
                "file_url": file.file_url,
                "file_type": file.file_type,
                "source": file.source,
                "uploaded_at": file.uploaded_at,
            }
            for file in f.files
        ],
    }

def get_all_folders_admin(db: Session):
    folders = db.query(MaterialFolder).order_by(MaterialFolder.created_at.desc()).all()
    return [folder_to_dict(f) for f in folders]

def get_materials_for_position(db: Session, position: str):
    folders = db.query(MaterialFolder).order_by(MaterialFolder.name.asc()).all()
    return [
        folder_to_dict(f)
        for f in folders
        if position in [p.strip() for p in (f.allowed_positions or "").split(",") if p.strip()]
    ]

def add_material_folder(db, name, description, allowed_positions):
    folder = MaterialFolder(name=name, description=description, allowed_positions=",".join(allowed_positions))
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder_to_dict(folder)

def edit_material_folder(db, folder_id, name, description, allowed_positions):
    folder = db.query(MaterialFolder).filter(MaterialFolder.id == folder_id).first()
    if not folder:
        return {"status": "error", "message": "Folder not found"}
    folder.name = name
    folder.description = description
    folder.allowed_positions = ",".join(allowed_positions)
    db.commit()
    db.refresh(folder)
    return folder_to_dict(folder)

def delete_material_folder(db, folder_id):
    folder = db.query(MaterialFolder).filter(MaterialFolder.id == folder_id).first()
    if not folder:
        return {"status": "error", "message": "Folder not found"}
    db.delete(folder)
    db.commit()
    return {"status": "success"}

def add_material_file(db, folder_id, name, file_url, file_type):
    folder = db.query(MaterialFolder).filter(MaterialFolder.id == folder_id).first()
    if not folder:
        return {"status": "error", "message": "Folder not found"}
    file = MaterialFile(folder_id=folder_id, name=name, file_url=file_url, file_type=file_type)
    db.add(file)
    db.commit()
    db.refresh(file)
    return {
        "id": file.id,
        "name": file.name,
        "file_url": file.file_url,
        "file_type": file.file_type,
        "uploaded_at": file.uploaded_at,
    }

def detect_link_type(url: str) -> str:
    url = url.lower()
    if "docs.google.com/document" in url:
        return "google_doc"
    if "docs.google.com/spreadsheets" in url:
        return "google_sheet"
    if "docs.google.com/presentation" in url:
        return "google_slide"
    if "drive.google.com" in url:
        return "google_drive"
    return "link"

def add_material_link(db, folder_id, name, url):
    folder = db.query(MaterialFolder).filter(MaterialFolder.id == folder_id).first()
    if not folder:
        return {"status": "error", "message": "Folder not found"}

    file_type = detect_link_type(url)
    file = MaterialFile(
        folder_id=folder_id,
        name=name,
        file_url=url,
        file_type=file_type,
        source="link",
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    return {
        "id": file.id,
        "name": file.name,
        "file_url": file.file_url,
        "file_type": file.file_type,
        "source": file.source,
        "uploaded_at": file.uploaded_at,
    }

def delete_material_file(db, file_id):
    file = db.query(MaterialFile).filter(MaterialFile.id == file_id).first()
    if not file:
        return {"status": "error", "message": "File not found"}
    db.delete(file)
    db.commit()
    return {"status": "success"}