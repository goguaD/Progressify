from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import auth
from database import engine, get_db, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Progressify API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(
            models.User.email == "admin@progressify.ge"
        ).first()
        if not existing:
            admin = models.User(
                firstname="Admin",
                lastname="Progressify",
                middlename=None,
                email="admin@progressify.ge",
                password_hash=auth.hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created: admin@progressify.ge / admin123")
        else:
            print("ℹ️  Admin user already exists.")
    finally:
        db.close()


seed_admin()


# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        middlename=user_data.middlename,
        email=user_data.email,
        password_hash=auth.hash_password(user_data.password),
        weight=user_data.weight,
        height=user_data.height,
        goal=user_data.goal,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/auth/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == credentials.email
    ).first()
    if not user or not auth.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


# ─── Admin Routes ─────────────────────────────────────────────────────────────

def require_admin(token: str, db: Session):
    payload = auth.decode_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    user = db.query(models.User).filter(
        models.User.id == int(payload["sub"])
    ).first()
    if not user:
        raise HTTPException(status_code=403, detail="Admin user not found")
    return user


@app.get("/admin/users", response_model=List[schemas.AdminUserOut])
def get_all_users(token: str, db: Session = Depends(get_db)):
    require_admin(token, db)
    return db.query(models.User).all()


@app.get("/")
def root():
    return {"message": "Progressify API is running"}
