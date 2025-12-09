from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import re

app = FastAPI(title="Velora API", version="2.0.0")

# CORS (Frontend farklı portta olacağı için izinler şart)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GÜVENLİK (BEARER TOKEN) ---
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Basit bir Token kontrolü. 
    Gerçek hayatta JWT decode edilir, burada token var mı diye bakıyoruz.
    Token formatı: "Bearer fake-token-12345"
    """
    token = credentials.credentials
    if not token.startswith("fake-token-"):
        raise HTTPException(status_code=403, detail="Geçersiz veya hatalı Token!")
    return token  # Token geçerliyse işlemi devam ettir

# --- VERİTABANI (RAM) ---
users_db = []
tasks_db = []
passwords_db = []
reminders_db = []

# --- MODELLER ---
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

class ReminderCreate(BaseModel):
    note: str
    time: str

class Reminder(ReminderCreate):
    id: str
    user_id: str

# --- YARDIMCI FONKSİYONLAR ---
def analyze_password_strength(password: str):
    strength = 0
    suggestions = []
    if len(password) >= 8: strength += 1
    else: suggestions.append("En az 8 karakter.")
    if re.search(r"[A-Z]", password): strength += 1
    if re.search(r"\d", password): strength += 1
    
    level = "Zayıf" if strength <= 1 else "Orta" if strength == 2 else "Güçlü"
    return level, suggestions

# --- ENDPOINTLER ---

@app.post("/auth/register", status_code=201, tags=["Auth"])
async def register(user: UserRegister):
    if any(u["email"] == user.email for u in users_db):
        raise HTTPException(400, "Bu e-posta zaten kayıtlı.")
    
    new_user = {
        "id": str(uuid4()),
        "email": user.email,
        "password": user.password,
        "full_name": user.full_name,
    }
    users_db.append(new_user)
    return {"mesaj": "Kayıt başarılı!", "user_id": new_user["id"]}

@app.post("/auth/login", tags=["Auth"])
async def login(user: UserLogin):
    u = next((x for x in users_db if x["email"] == user.email and x["password"] == user.password), None)
    if not u:
        raise HTTPException(401, "Geçersiz bilgiler.")
    
    # Basit bir token oluşturuyoruz
    fake_token = f"fake-token-{u['id']}"
    return {"mesaj": "Giriş başarılı!", "user_id": u["id"], "access_token": fake_token}

# --- KORUMALI ENDPOINTLER (Token Zorunlu) ---
# dependencies=[Depends(verify_token)] diyerek kilidi takıyoruz.

@app.post("/api/tasks/{uid}", tags=["Tasks"], dependencies=[Depends(verify_token)])
async def add_task(uid: str, data: TaskCreate):
    t = Task(id=str(uuid4()), user_id=uid, **data.dict())
    tasks_db.append(t)
    return t

@app.get("/api/tasks/{uid}", response_model=List[Task], tags=["Tasks"], dependencies=[Depends(verify_token)])
async def get_tasks(uid: str):
    return [t for t in tasks_db if t.user_id == uid]

@app.post("/api/passwords/{uid}", tags=["Passwords"], dependencies=[Depends(verify_token)])
async def add_pass(uid: str, data: PasswordCreate):
    strength, sugg = analyze_password_strength(data.password)
    p = Password(id=str(uuid4()), user_id=uid, strength=strength, **data.dict())
    passwords_db.append(p)
    return {"mesaj": "Eklendi", "data": p}

@app.get("/api/passwords/{uid}", response_model=List[Password], tags=["Passwords"], dependencies=[Depends(verify_token)])
async def get_pass(uid: str):
    return [p for p in passwords_db if p.user_id == uid]

@app.post("/api/reminders/{uid}", tags=["Reminders"], dependencies=[Depends(verify_token)])
async def add_rem(uid: str, data: ReminderCreate):
    r = Reminder(id=str(uuid4()), user_id=uid, **data.dict())
    reminders_db.append(r)
    return r

@app.get("/api/reminders/{uid}", response_model=List[Reminder], tags=["Reminders"], dependencies=[Depends(verify_token)])
async def get_rem(uid: str):
    return [r for r in reminders_db if r.user_id == uid]
