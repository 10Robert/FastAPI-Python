from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from models import Users
from starlette import status
from typing import Annotated
from database import db_dependency
from fastapi.security import OAuth2PasswordRequestForm
from schemas.schema import CreateUserRequest, PartialUpdateUserRequest, Token
from utils.crud import bcrypt_context, create_acess_token, authenticate_user, alter_user, user_dependency, create_users

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(  db: db_dependency,
                        create_user_request: CreateUserRequest):
    create_users(db, create_user_request)
 
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
                      user_request: CreateUserRequest, user_id: int):
    alter_user(db, user_request, user_id)
    return db.query(Users).filter(Users.id == user_id).first()  
      
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
            if user_request.password is None:
                user_model.hashed_password = user_model.hashed_password
            else:
                user_model.hashed_password = bcrypt_context.hash(user_request.password)# type: ignore
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    
    db.add(user_model)
    db.commit()