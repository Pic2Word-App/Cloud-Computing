from typing import List, Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Response, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .database import models, schemas, crud
from .database.database import SessionLocal, engine
from .database.crud import get_current_user
import os
from google.cloud import storage
import uvicorn
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

storage_client = storage.Client()
bucket_name = os.getenv("BUCKET_NAME")
bucket = storage_client.bucket(bucket_name)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users", response_model=List[schemas.Users])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@app.post("/register", response_model=schemas.Users)
def register(registerUser: schemas.RegisterUser, db: Session = Depends(get_db)):
    return crud.register(db=db, registerUser=registerUser)
  

@app.post("/login", response_model=dict())
def login_for_access_token(loginUser: schemas.LoginUser, db: Session = Depends(get_db)):
    authenticated_user = crud.authenticate_user(db, loginUser)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = crud.create_access_token(data={"sub": authenticated_user.user_id})
    
    return {
      "user": crud.get_user_by_id(db, authenticated_user.user_id),
      "access_token": access_token, 
      "token_type": "bearer"
    }


@app.get("/users/me", response_model=dict())
def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

  
@app.put("/users/me", response_model=schemas.Users)
def update_user(user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.update_user(db, user, current_user)


@app.post("/translate")
def translate_text(target: str, text: str):
    return crud.translate_text(target, text)


@app.post("/upload/", response_model=dict())
def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), prediction: str = None, translate: str = None):
    return crud.upload_image(file, db, current_user, prediction, translate)
  

@app.get("/images/me", response_model=List[dict])
def get_images(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.get_images(db, current_user["user_id"])
  
  
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)