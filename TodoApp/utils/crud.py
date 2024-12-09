from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette import status
from typing import Annotated
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
import json
from ..models import Users
from sqlalchemy.exc import SQLAlchemyError

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = "132ln21bl124jjsahahhajj3j40r1klnaafa03naln2lnlabfaf"
ALGORITHM = "HS256"

def verify_password(plain_password, hash_password):
    return bcrypt_context.verify(plain_password, hash_password)

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
    
user_dependency = Annotated[dict, Depends(get_current_user)]

def authenticate_user(username: str, password: str, db) :
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

def alter_user(db, user_request, user_id):
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if user:
            user.email = user_request.email # type: ignore
            user.first_name = user_request.first_name # type: ignore
            user.username = user_request.username # type: ignore
            user.last_name = user_request.last_name # type: ignore
            user.role = user_request.role # type: ignore
            user.hashed_password = bcrypt_context.hash(user_request.password) # type: ignore
            user.phone_number = user_request.phone_number
            db.add(user)
            db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

def create_users(db, create_user_request):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True,
        phone_number = create_user_request.phone_number
    )
    db.add(create_user_model)
    db.commit()
