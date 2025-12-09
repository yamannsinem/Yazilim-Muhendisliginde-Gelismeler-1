from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import re

# Proje Adı Güncellendi
app = FastAPI(title="Velora API", version="1.0.0")

# --- AYARLAR ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOCK VERİTABANI ---
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
    else: suggestions.append("Şifre en az 8 karakter olmalı.")
    if re.search(r"[A-Z]", password): strength += 1
    else: suggestions.append("En az bir büyük harf ekle.")
    if re.search(r"[a-z]", password): strength += 1
    else: suggestions.append("En az bir küçük harf ekle.")
    if re.search(r"\d", password): strength += 1
    else: suggestions.append("En az bir rakam ekle.")
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): strength += 1
    else: suggestions.append("En az bir özel karakter ekle.")
    level = "Zayıf" if strength <= 2 else "Orta" if strength <= 4 else "Güçlü"
    return level, suggestions

# --- ENDPOINTLER ---

@app.get("/")
async def root():
    return {"mesaj": "Velora API çalışıyor 🚀"}

# 1. Authentication
@app.post("/auth/register", status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register(user: UserRegister):
    if any(u["email"] == user.email for u in users_db):
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı.")
    
    new_user = {
        "id": str(uuid4()),
        "email": user.email,
        "password": user.password,
        "full_name": user.full_name,
    }
    users_db.append(new_user)
    return {"mesaj": "Velora'ya hoş geldin!", "user_id": new_user["id"]}

@app.post("/auth/login", tags=["Authentication"])
async def login(user: UserLogin):
    user_data = next((u for u in users_db if u["email"] == user.email and u["password"] == user.password), None)
    if not user_data:
        raise HTTPException(status_code=401, detail="E-posta veya şifre hatalı!")
    
    return {"mesaj": "Giriş başarılı", "user_id": user_data["id"], "token": f"fake-jwt-{user_data['id']}"}

# 2. Görevler
@app.post("/api/tasks/{user_id}", response_model=Task, tags=["Tasks"])
async def create_task(user_id: str, task: TaskCreate):
    new_task = Task(id=str(uuid4()), user_id=user_id, **task.dict())
    tasks_db.append(new_task)
    return new_task

@app.get("/api/tasks/{user_id}", response_model=List[Task], tags=["Tasks"])
async def get_tasks(user_id: str):
    return [t for t in tasks_db if t.user_id == user_id]

# 3. Şifreler
@app.post("/api/passwords/{user_id}", tags=["Passwords"])
async def add_password(user_id: str, data: PasswordCreate):
    level, suggestions = analyze_password_strength(data.password)
    new_pwd = Password(
        id=str(uuid4()),
        user_id=user_id,
        account=data.account,
        username=data.username,
        password=data.password,
        strength=level,
    )
    passwords_db.append(new_pwd)
    return {"mesaj": "Parola kasaya eklendi!", "strength": level, "suggestions": suggestions, "data": new_pwd}

@app.get("/api/passwords/{user_id}", response_model=List[Password], tags=["Passwords"])
async def get_passwords(user_id: str):
    return [p for p in passwords_db if p.user_id == user_id]

# 4. Hatırlatıcılar
@app.post("/api/reminders/{user_id}", response_model=Reminder, tags=["Reminders"])
async def create_reminder(user_id: str, data: ReminderCreate):
    new_reminder = Reminder(id=str(uuid4()), user_id=user_id, **data.dict())
    reminders_db.append(new_reminder)
    return new_reminder

@app.get("/api/reminders/{user_id}", response_model=List[Reminder], tags=["Reminders"])
async def get_reminders(user_id: str):
    return [r for r in reminders_db if r.user_id == user_id]
