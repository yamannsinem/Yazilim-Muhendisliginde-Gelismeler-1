from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import re

app = FastAPI(title="Velora API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

users_db = []
tasks_db = []
passwords_db = []
reminders_db = []

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

def analyze_password_strength(password: str):
    strength = 0
    rules = [
        (r"[A-Z]", "Büyük harf ekle."),
        (r"[a-z]", "Küçük harf ekle."),
        (r"\d", "Rakam ekle."),
        (r"[!@#$%^&*(),.?\":{}|<>]", "Özel karakter ekle.")
    ]
    suggestions = []

    if len(password) < 8:
        suggestions.append("En az 8 karakter olmalı.")
    else:
        strength += 1

    for pattern, warn in rules:
        if re.search(pattern, password):
            strength += 1
        else:
            suggestions.append(warn)

    level = "Zayıf" if strength <= 2 else "Orta" if strength <= 4 else "Güçlü"
    return level, suggestions

@app.post("/auth/register", status_code=201)
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

@app.post("/auth/login")
async def login(user: UserLogin):
    u = next((x for x in users_db if x["email"] == user.email and x["password"] == user.password), None)
    if not u:
        raise HTTPException(401, "Geçersiz bilgiler.")
    return {"mesaj": "Giriş başarılı!", "user_id": u["id"], "token": f"fake-{u['id']}"}

@app.post("/api/tasks/{uid}")
async def add_task(uid: str, data: TaskCreate):
    t = Task(id=str(uuid4()), user_id=uid, **data.dict())
    tasks_db.append(t)
    return t

@app.get("/api/tasks/{uid}", response_model=List[Task])
async def get_tasks(uid: str):
    return [t for t in tasks_db if t.user_id == uid]

@app.post("/api/passwords/{uid}")
async def add_pass(uid: str, data: PasswordCreate):
    strength, sugg = analyze_password_strength(data.password)
    p = Password(id=str(uuid4()), user_id=uid, strength=strength, **data.dict())
    passwords_db.append(p)
    return {"mesaj": "Kasa’ya eklendi!", "data": p, "öneriler": sugg}

@app.get("/api/passwords/{uid}", response_model=List[Password])
async def get_pass(uid: str):
    return [p for p in passwords_db if p.user_id == uid]

@app.post("/api/reminders/{uid}")
async def add_rem(uid: str, data: ReminderCreate):
    r = Reminder(id=str(uuid4()), user_id=uid, **data.dict())
    reminders_db.append(r)
    return r

@app.get("/api/reminders/{uid}", response_model=List[Reminder])
async def get_rem(uid: str):
    return [r for r in reminders_db if r.user_id == uid]
