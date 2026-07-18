from fastapi import FastAPI, Depends, HTTPException , Query , Form , UploadFile , Body
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from schemas import *
from crud import *
from fastapi.middleware.cors import CORSMiddleware
from dependencies import *
from typing import List
import models
import gspread
from google.oauth2.service_account import Credentials
from authentication import *
from utils import upload_to_cloudinary , upload_file_to_cloudinary
import json
import os


app = FastAPI(title="ADA Hub User Auth API")

SPREADSHEET_NAME = "NTT Azerbaijan | 26.27 "
GLOBAL_WORKSHEET_NAME = "LC Global Ranking💪"
NATIONAL_WORKSHEET_NAME = "LC Monthly Ranking🔥"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

google_creds = json.loads(
    os.getenv("GOOGLE_CREDENTIALS")
)

creds = Credentials.from_service_account_info(
    google_creds,
    scopes=SCOPES
)

def get_sheets():
    google_creds = json.loads(
        os.getenv("GOOGLE_CREDENTIALS")
    )

    creds = Credentials.from_service_account_info(
        google_creds,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    global_sheet = client.open(
        os.getenv("SPREADSHEET_NAME")
    ).worksheet(
        os.getenv("GLOBAL_WORKSHEET_NAME")
    )

    national_sheet = client.open(
        os.getenv("SPREADSHEET_NAME")
    ).worksheet(
        os.getenv("NATIONAL_WORKSHEET_NAME")
    )

    return global_sheet, national_sheet

def get_baku_ada_data():
    global_sheet, national_sheet = get_sheets()
    global_data = global_sheet.get("B4:D28")
    national_data = national_sheet.get("C5:E8")  # get Rank, Local Committee, APD
    globalRank = 0
    nationalRank = 0
    apd = 0
    for row in global_data:
        if "Baku ADA" in row[1]:
            globalRank = row[0]
            apd = row[2]
        
    for row in national_data:
        if "Baku ADA" in row[1]:
            nationalRank=row[0]
    return {"global_rank":globalRank , "national_rank":nationalRank , "Approveds":apd}

origins = [
    "http://localhost:3000",
    # "https://ada-ca8dbde28-aqillous.vercel.app/",
    "http://localhost:5173",
    os.getenv("FRONTEND_URL")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in origins if o],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register", response_model=dict)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    result = register_user(
    db,
    request.email,
    request.password,
    False,
    request.name,
    request.surname
)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/login", response_model=dict)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, request.email, request.password)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/admin")
def adminDashboard(admin=Depends(get_current_admin)):
    # return user info for admin only
    return {
        "user_id": admin.get("sub"),
        "email": admin.get("email"),
        "is_admin": admin.get("is_admin")
    }

@app.get("/users" , response_model=List[AllUsersResponse])
def getAllUsers(admin=Depends(get_current_admin) , db: Session = Depends(get_db)):
    return all_users(db)

@app.delete("/users/{id}")
def deleteUser(id:int , admin=Depends(get_current_admin) , db:Session= Depends(get_db)):
    return delete_user(db , id)

@app.patch("/users/{id}/admin")
def changeAdminStatus(id:int , is_admin:bool = Query(...) , admin=Depends(get_current_admin) , db:Session = Depends(get_db)):
    return edit_user(db , id , is_admin) 

@app.post("/users/add")
def addUser(request:AddUserRequest , admin=Depends(get_current_admin) , db:Session = Depends(get_db)):
    return register_user(db , request.email , request.password , request.is_admin)

@app.post("/admin/calEvent")
def addCalendarEvent(request:CalendarEventRequest , db: Session = Depends(get_db) , admin=Depends(get_current_admin)):
    return add_calendar_event(db,request.event_date , request.event_time , request.event_name)

@app.get("/allCalendarEvents" , response_model=List[AllCalendarEventsResponse])
def getAllCalendarEvents(db:Session = Depends(get_db)):
    return all_calendar_events(db)

@app.delete("/admin/calEvent/{id}")
def deleteCalendarEvent(id:int , admin=Depends(get_current_admin) , db: Session = Depends(get_db)):
    return delete_calendar_event(db , id)

@app.patch("/admin/calEvent/{id}/edit")
def editCalendarEvent(id:int , request:CalendarEventRequest , admin= Depends(get_current_admin) , db:Session= Depends(get_db)):
    return edit_calendar_event(db , id , request.event_name ,request.event_date , request.event_time)

@app.post("/admin/news")
def addNews(
    request:AddNewsRequest,
    db:Session=Depends(get_db),
    admin=Depends(get_current_admin)
):
    return add_news(
        db,
        request.news_header,
        request.news_content,
        request.news_short
    )

@app.get("/allNews" , response_model=List[AllNewsResponse])
def getAllNews(db:Session=Depends(get_db)):
    return all_news(db)

@app.delete("/admin/news/{id}")
def deleteNews(id:int , admin=Depends(get_current_admin) , db:Session = Depends(get_db)):
    return delete_news(db , id)

@app.patch("/admin/news/{id}/edit")
def editNews(id:int , request:AddNewsRequest, admin=Depends(get_current_admin) , db:Session = Depends(get_db)):
    return edit_news(db , id , request.news_header , request.news_content)

@app.get("/lcData")
def getLcData():
    return get_baku_ada_data()

@app.post("/refresh")
def refresh_token(request: RefreshTokenRequest):
    payload = verify_token(request.refresh_token)
    user_id = payload["sub"]

    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        is_admin = user.is_admin
    finally:
        db.close()

    new_access = create_access_token({"sub": str(user_id), "is_admin": is_admin})
    new_refresh = create_refresh_token({"sub": str(user_id), "is_admin": is_admin})

    return {"access_token": new_access, "refresh_token": new_refresh}

@app.post("/admin/store/product/add")
async def addProduct( name:str = Form(...), price:str = Form(...) , image:UploadFile =None, admin=Depends(get_current_admin) , db:Session = Depends(get_db)):
    image_url = None
    if image:
        try:
            image_url = upload_to_cloudinary(image)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image upload failed: {str(e)}")
    
    return add_product(db , name , price , image_url)

@app.get("/store/products" , response_model=list[ProductOut])
def getAllProducts(db:Session=Depends(get_db)):
    return get_all_products(db)

@app.delete("/admin/store/product/{id}")
def deleteProduct(id:int, admin=Depends(get_current_admin), db:Session=Depends(get_db)):
    return delete_product(db, id) 

@app.patch("/admin/store/product/{id}/edit")
async def editProduct(
    id: int,
    name: str = Form(...),
    price: str = Form(...),
    image: UploadFile = None,  # <-- matches frontend "image"
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    product = get_product(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if image:
        try:
            uploaded_url = upload_to_cloudinary(image)  # returns Cloudinary URL
            product.image_url = uploaded_url
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image upload failed: {str(e)}")

    product.name = name
    product.price = price
    db.commit()
    db.refresh(product)
    return product

@app.post("/store/addOrder")
def createOrder(order_data: OrderSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    user_id = user["sub"]  # extract user id from JWT
    order = create_order(db, user_id, order_data)
    return {"status": "success", "order_id": order.id}

@app.get("/admin/store/allOrders" , response_model=list[OrderOut])
def getAllOrders(admin = Depends(get_current_admin)  , db:Session = Depends(get_db)):
    return(get_all_orders(db))

@app.delete("/admin/store/order/{id}")
def deleteOrder(id:int , admin = Depends(get_current_admin) ,db:Session = Depends(get_db)):
    return delete_order(db , id)

@app.patch("/admin/store/order/{id}/edit")
def editOrderStatus(
    id: int,
    data: OrderStatusUpdate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    result = change_order_status(db, id, data.status)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.get("/admin/store/dashboard")
def dashboard(admin= Depends(get_current_admin), db: Session = Depends(get_db)):
    return get_dashboard_stats(db)

@app.get("/me")
def getMe(user=Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = int(user.get("sub"))
    data = get_me(db, user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data

@app.patch("/profile")
def updateProfile(request: UpdateProfileRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = int(user.get("sub"))
    result = update_profile(db, user_id, request.name, request.surname)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@app.patch("/users/{id}/position")
def changeUserPosition(
    id: int,
    request: UpdateUserPositionRequest,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    result = update_user_position(db, id, request.current_position)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@app.patch("/profile/password")
def changePassword(request: ChangePasswordRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = change_password(db, int(user.get("sub")), request.current_password, request.new_password)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/my-orders")
def getMyOrders(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_orders(db, int(user.get("sub")))


@app.get("/vps")
def getAllVPs(db: Session = Depends(get_db)):
    return get_all_vps(db)
 
@app.post("/admin/vps/add")
async def addVP(
    name: str = Form(...),
    position: str = Form(...),
    image: UploadFile = None,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    image_url = None
    if image:
        try:
            image_url = upload_to_cloudinary(image)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image upload failed: {str(e)}")
    return add_vp(db, name, position, image_url)
 
@app.patch("/admin/vps/{id}/edit")
async def editVP(
    id: int,
    name: str = Form(...),
    position: str = Form(...),
    image: UploadFile = None,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    vp = db.query(models.VP).filter(models.VP.id == id).first()
    if not vp:
        raise HTTPException(status_code=404, detail="VP not found")
 
    image_url = None
    if image:
        try:
            image_url = upload_to_cloudinary(image)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image upload failed: {str(e)}")
 
    result = edit_vp(db, id, name, position, image_url)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result
 
@app.delete("/admin/vps/{id}")
def deleteVP(id: int, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    result = delete_vp(db, id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


# ---------------------------------------------------------------------------
# Materials — member side: access is by position OR by email, no hard gate
# ---------------------------------------------------------------------------

@app.get("/materials")
def getMaterials(user=Depends(get_current_user), db: Session = Depends(get_db)):
    me = db.query(models.User).filter(models.User.id == int(user["sub"])).first()
    if not me:
        raise HTTPException(status_code=404, detail="User not found")
    # NOTE: no longer requires current_position — an admin can grant access
    # purely by email even if the user has no position assigned.
    return get_materials_for_user(db, me.current_position or "", me.email)


# ---------------------------------------------------------------------------
# Materials — admin side: full tree, nested folders, appearance, email access
# ---------------------------------------------------------------------------

@app.get("/admin/materials/folders")
def adminGetFolders(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    return get_all_folders_admin(db)

@app.post("/admin/materials/folders")
def adminAddFolder(request: MaterialFolderCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    result = add_material_folder(
        db,
        request.name,
        request.description,
        request.allowed_positions,
        request.allowed_emails,
        request.color,
        request.icon,
        request.parent_id,
    )
    if isinstance(result, dict) and result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.patch("/admin/materials/folders/{id}")
def adminEditFolder(id: int, request: MaterialFolderCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    result = edit_material_folder(
        db,
        id,
        request.name,
        request.description,
        request.allowed_positions,
        request.allowed_emails,
        request.color,
        request.icon,
        request.parent_id,
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@app.delete("/admin/materials/folders/{id}")
def adminDeleteFolder(id: int, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    return delete_material_folder(db, id)

@app.post("/admin/materials/folders/{id}/files")
async def adminAddFile(id: int, file: UploadFile, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        file_url = upload_file_to_cloudinary(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    return add_material_file(db, id, file.filename, file_url, ext)

@app.delete("/admin/materials/files/{id}")
def adminDeleteFile(id: int, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    return delete_material_file(db, id)

@app.post("/admin/materials/folders/{id}/links")
def adminAddLink(id: int, request: MaterialLinkCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    result = add_material_link(db, id, request.name, request.url)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result
