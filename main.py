from typing import List

from fastapi import Depends, FastAPI, Response, status, HTTPException
from sqlalchemy.orm import Session

from .database import models, schemas, crud
from .database.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/", response_model=List[schemas.Users])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.Users)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/register/", response_model=schemas.Users)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.register(db=db, user=user)


# @app.patch("/expenses/{expense_id}", response_model=schemas.Expense)
# def update_expense(
#     expense_id: int,
#     expense_partial: schemas.ExpenseUpdate,
#     db: Session = Depends(get_db),
# ):
#     return crud.update_expense(db, expense_id, expense_partial)


# @app.delete("/expenses/{expense_id}", response_class=Response)
# def delete_expense(expense_id: int, db: Session = Depends(get_db)):
#     crud.delete_expense(db, expense_id)
#     return Response(status_code=status.HTTP_204_NO_CONTENT)