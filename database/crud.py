from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt
from fastapi import HTTPException, status, Depends, UploadFile, Header, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from sqlalchemy import desc
from passlib.context import CryptContext
from .database import SessionLocal
from google.cloud import storage
import os
from google.cloud import translate_v2 as translate

from . import models, schemas

storage_client = storage.Client()
bucket_name = os.getenv("BUCKET_NAME")
bucket = storage_client.bucket(bucket_name)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "apakek"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

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
        user =  (
            db.query(models.Users)
            .filter(models.Users.user_id == user_id)
            .first()
          )
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "jenis_kelamin": user.jenis_kelamin,
            "tanggal_lahir": user.tanggal_lahir,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    except:
        raise HTTPException(
            status_code=404, detail=f"User not found with ID {user_id}"
        )


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, loginUser: schemas.UserLoginSchema):
    user = db.query(models.Users).filter(models.Users.email == loginUser.email).first()
    if not user:
        return False
    if not verify_password(loginUser.password, user.password):
        return False
    return user


def register(db: Session, registerUser: schemas.UserSchema):
    #check if email already exists
    user_exists = db.query(models.Users).filter(models.Users.email == registerUser.email).first()
    if user_exists:
        raise HTTPException(
            status_code=400, detail="Email already registered"
        )
    user_data = {
        "username": registerUser.username,
        "email": registerUser.email,
        "password": get_password_hash(registerUser.password),
    }
    db_user = models.Users(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
  
  
def get_user(db, user_id: int):
    if user_id in db:
        user_dict = db[user_id]
        return models.Users(**user_dict)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
  
  
async def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_scheme)]):
    token = request.headers.get("Authorization")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_by_id(SessionLocal(), user_id)
    if user is None:
        raise credentials_exception
    return user
  
  
def update_user(db: Session, user: schemas.UserUpdate, current_user: dict):
    user_data = user.dict(exclude_unset=True)
    user_data["updated_at"] = datetime.now(timezone.utc)
    db_user = db.query(models.Users).filter(models.Users.user_id == current_user.get("user_id")).first()
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user
    

def upload_image(file: UploadFile, db: Session, current_user: dict, prediction: str = None, translate: str = None):
    blob_path = f"image/{file.filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_file(file.file)
    image_data = {
        "user_id": current_user.get("user_id"),
        "image_url": f"https://storage.googleapis.com/{bucket_name}/{file.filename}",
        "image_name": file.filename,
        "prediction": prediction,
        "translate": translate
    }
    db_image = models.Image(**image_data)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return image_data
  

def translate_text(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target, source_language="id")

    return result


def get_images(db: Session, user_id: int):
    images = db.query(models.Image).filter(models.Image.user_id == user_id).all()
    
    return [
        {
            "image_id": image.image_id,
            "user_id": image.user_id,
            "image_url": image.image_url,
            "image_name": image.image_name,
            "prediction": image.prediction,
            "translate": image.translate
        }
        for image in images
    ]
    

def get_image(image_name: str):
    blob = bucket.blob(f"image/{image_name}")
    return blob.download_as_bytes()