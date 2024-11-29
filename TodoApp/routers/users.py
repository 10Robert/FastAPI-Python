from fastapi import APIRouter, HTTPException
from models import Users
from starlette import status
from database import db_dependency
from utils.crud import user_dependency
from schemas.schema import UserVerification

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
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