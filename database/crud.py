from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from passlib.context import CryptContext

from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Users)
        .order_by(desc("user_id"))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_by_id(db: Session, user_id: int):
    try:
        return (
            db.query(models.Users)
            .filter(models.Users.user_id == user_id)
            .first()
          )
    except:
        raise HTTPException(
            status_code=404, detail=f"User not found with ID {user_id}"
        )


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def register(db: Session, user: schemas.UserCreate):
    #check if email already exists
    user_exists = db.query(models.Users).filter(models.Users.email == user.email).first()
    if user_exists:
        raise HTTPException(
            status_code=400, detail="Email already registered"
        )
    user_data = user.dict()
    user_data["password"] = get_password_hash(user_data["password"])
    user_data["created_at"] = datetime.now(timezone.utc)
    user_data["updated_at"] = datetime.now(timezone.utc)
    db_user = models.Users(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, user_id: int, user_partial: schemas.UserUpdate
):
    user = (
        db.query(models.Users).filter(models.Users.user_id == user_id).first()
    )
    user_data = user_partial.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = (
        db.query(models.Users).filter(models.Users.user_id == user_id).first()
    )
    if user:
        db.delete(user)
        db.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f" not found with ID {user_id}"
        )