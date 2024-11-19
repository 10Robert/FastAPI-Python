from datetime import datetime, timezone, timedelta
from email.policy import HTTP
from secrets import token_bytes
import bcrypt
from click import Option
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Users
from starlette import status
from passlib.context import CryptContext
from typing import Annotated, Optional
from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
import json


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "132ln21bl124jjsahahhajj3j40r1klnaafa03naln2lnlabfaf"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class PartialUpdateUserRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None
    role: str | None = None



class Token(BaseModel):
    access_token: str
    token_type: str

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

def authenticate_user(username: str, password: str, db) -> bool:
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_acess_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = json.dumps(datetime.now(timezone.utc).isoformat())
    encode.update({"ext": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") #type: ignore
        user_id: int = payload.get("id") # type: ignore
        user_role: str = payload.get("role") #type: ignore
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Could not validade user.")
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Unable to validate the user')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(  db: db_dependency,
                        create_user_request: CreateUserRequest):

    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True
    )

    db.add(create_user_model)
    db.commit()
 
@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def read_by_user(db: db_dependency, user_id: int = Path(gt=0)):
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if user:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
    
    
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_users(db: db_dependency):
    try:
        users = db.query(Users).all()
        if users:
            return users
        else:
            raise HTTPException(status_code=status.HTPP_404_NOT_FOUND, detail="Users not found.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
    
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, 
                      user_id: int = Path(gt=0)):
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if user:
            db.query(Users).filter(Users.id == user_id).delete()
            db.commit()
        else: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error.")
    
@router.put("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(db: db_dependency, 
                      user_request: CreateUserRequest,
                      user_id: int = Path(gt=0)):
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if user:
            user.email = user_request.email # type: ignore
            user.first_name = user_request.first_name # type: ignore
            user.username = user_request.username # type: ignore
            user.last_name = user_request.last_name # type: ignore
            user.role = user_request.role # type: ignore
            user.hashed_password = bcrypt_context.hash(user_request.password) # type: ignore

            db.add(user)
            db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
            
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Could not valdiade user")
    token = create_acess_token(user.username, user.id, user.role,timedelta(minutes=20)) #type: ignore
    return {"access_token": token, "token_type": "bearer"}


@router.patch('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def partial_update_user(db: db_dependency,
                         user_request: PartialUpdateUserRequest,
                         user_id: int = Path(gt=0)):
    try:
        user_model = db.query(Users).filter(Users.id == user_id).first()
        if user_model:
            user_model.email = user_request.email or user_model.email# type: ignore
            user_model.first_name = user_request.first_name or user_model.first_name# type: ignore
            user_model.username = user_request.username or user_model.username# type: ignore
            user_model.last_name = user_request.last_name or user_model.last_name# type: ignore
            user_model.role = user_request.role or user_model.role# type: ignore
            user_model.hashed_password = bcrypt_context.hash(user_request.password) or user_model.hashed_password# type: ignore        
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")