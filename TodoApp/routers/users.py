from email.policy import HTTP
import bcrypt
from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .auth import get_current_user
from models import Users
from starlette import status
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

bycrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class UserVerification(BaseModel):
     password: str 
     new_password: str  = Field(min_length=6)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()

@router.patch("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                        user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bycrypt_context.verify(user_verification.password, user_model.hashed_password): #type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password change")
    user_model.hashed_password = bycrypt_context.hash(user_verification.new_password) #type: ignore
    db.add(user_model)
    db.commit()