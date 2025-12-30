import os
import re
from uuid import uuid4
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- SQLALCHEMY (Veritabanı) ---
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI(title="Velora API", version="3.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://velora:velorapass@localhost/veloradb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELLER ---
class DBUser(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)

class DBTask(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String, nullable=True)

class DBPassword(Base):
    __tablename__ = "passwords"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    account = Column(String)
    username = Column(String)
    password = Column(String)
    strength = Column(String)

class DBReminder(Base):
    __tablename__ = "reminders"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    note = Column(String)
    time = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- PYDANTIC ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class Task(TaskCreate):
    id: str
    user_id: str
    class Config:
        orm_mode = True

class PasswordCreate(BaseModel):
    account: str
    username: str
    password: str

class Password(BaseModel):
    id: str
    user_id: str
    account: str
    username: str
    password: str
    strength: str
    class Config:
        orm_mode = True

class ReminderCreate(BaseModel):
    note: str
    time: str

class Reminder(ReminderCreate):
    id: str
    user_id: str
    class Config:
        orm_mode = True

# --- GÜVENLİK ---
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token.startswith("fake-token-"):
        raise HTTPException(status_code=403, detail="Geçersiz Token!")
    return token

def analyze_password_strength(password: str):
    strength = 0
    if len(password) >= 8: strength += 1
    if re.search(r"[A-Z]", password): strength += 1
    if re.search(r"\d", password): strength += 1
    return "Zayıf" if strength <= 1 else "Orta" if strength == 2 else "Güçlü"

# --- ENDPOINTLER ---

@app.post("/auth/register", status_code=201, tags=["Auth"])
async def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(DBUser).filter(DBUser.email == user.email).first()
    if existing_user:
        raise HTTPException(400, "Bu e-posta zaten kayıtlı.")
    
    new_user = DBUser(id=str(uuid4()), email=user.email, password=user.password, full_name=user.full_name)
    db.add(new_user)
    db.commit()
    return {"mesaj": "Kayıt başarılı!", "user_id": new_user.id}

@app.post("/auth/login", tags=["Auth"])
async def login(user: UserLogin, db: Session = Depends(get_db)):
    u = db.query(DBUser).filter(DBUser.email == user.email, DBUser.password == user.password).first()
    if not u:
        raise HTTPException(401, "Geçersiz bilgiler.")
    return {"mesaj": "Giriş başarılı!", "user_id": u.id, "access_token": f"fake-token-{u.id}"}

# --- TASKS ---
@app.post("/api/tasks/{uid}", tags=["Tasks"], dependencies=[Depends(verify_token)])
async def add_task(uid: str, data: TaskCreate, db: Session = Depends(get_db)):
    t = DBTask(id=str(uuid4()), user_id=uid, title=data.title, description=data.description)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@app.get("/api/tasks/{uid}", response_model=List[Task], tags=["Tasks"], dependencies=[Depends(verify_token)])
async def get_tasks(uid: str, db: Session = Depends(get_db)):
    return db.query(DBTask).filter(DBTask.user_id == uid).all()

# --- PASSWORDS (GÜNCELLENDİ: Silme ve Düzenleme Eklendi) ---
@app.post("/api/passwords/{uid}", tags=["Passwords"], dependencies=[Depends(verify_token)])
async def add_pass(uid: str, data: PasswordCreate, db: Session = Depends(get_db)):
    strength = analyze_password_strength(data.password)
    p = DBPassword(id=str(uuid4()), user_id=uid, strength=strength, **data.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"mesaj": "Eklendi", "data": p}

@app.get("/api/passwords/{uid}", response_model=List[Password], tags=["Passwords"], dependencies=[Depends(verify_token)])
async def get_pass(uid: str, db: Session = Depends(get_db)):
    return db.query(DBPassword).filter(DBPassword.user_id == uid).all()

# SİLME (DELETE)
@app.delete("/api/passwords/{uid}/{item_id}", tags=["Passwords"], dependencies=[Depends(verify_token)])
async def delete_pass(uid: str, item_id: str, db: Session = Depends(get_db)):
    item = db.query(DBPassword).filter(DBPassword.id == item_id, DBPassword.user_id == uid).first()
    if not item:
        raise HTTPException(404, "Kayıt bulunamadı")
    db.delete(item)
    db.commit()
    return {"mesaj": "Silindi"}

# GÜNCELLEME (PUT)
@app.put("/api/passwords/{uid}/{item_id}", tags=["Passwords"], dependencies=[Depends(verify_token)])
async def update_pass(uid: str, item_id: str, data: PasswordCreate, db: Session = Depends(get_db)):
    item = db.query(DBPassword).filter(DBPassword.id == item_id, DBPassword.user_id == uid).first()
    if not item:
        raise HTTPException(404, "Kayıt bulunamadı")
    
    item.account = data.account
    item.username = data.username
    item.password = data.password
    item.strength = analyze_password_strength(data.password)
    
    db.commit()
    db.refresh(item)
    return {"mesaj": "Güncellendi", "data": item}

# --- REMINDERS ---
@app.post("/api/reminders/{uid}", tags=["Reminders"], dependencies=[Depends(verify_token)])
async def add_rem(uid: str, data: ReminderCreate, db: Session = Depends(get_db)):
    r = DBReminder(id=str(uuid4()), user_id=uid, **data.dict())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@app.get("/api/reminders/{uid}", response_model=List[Reminder], tags=["Reminders"], dependencies=[Depends(verify_token)])
async def get_rem(uid: str, db: Session = Depends(get_db)):
    return db.query(DBReminder).filter(DBReminder.user_id == uid).all()
