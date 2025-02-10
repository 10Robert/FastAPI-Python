from datetime import timedelta
from typing import Literal
from .utils import *
from ..database import get_db
from ..utils.crud import get_current_user, authenticate_user, ALGORITHM, create_acess_token, SECRET_KEY
from ..main import app
from starlette import status
from ..models import Users
from jose import jwt
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = overreide_get_user

def test_authenticate_user(test_user) -> None:
    db = TestingSessionLocal()
    
    authenticated_user: Users | Literal[False] = authenticate_user(test_user.username, "test_123", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username #type: ignore
    
    non_existent_user = authenticate_user("Robert", "123", db)
    assert non_existent_user is False

    wrong_passaword_user = authenticate_user(test_user.username, "test_1234", db)
    assert wrong_passaword_user is False

def test_create_access_token():
    username = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)

    token = create_acess_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})

    assert decoded_token['id'] == user_id
    assert decoded_token['sub'] == username
    assert decoded_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {"sub": "Robert_10", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    
    assert user == {"username": "Robert_10", "id": 1, "role": "admin"}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode: dict[str, str] = {"role": "user"}

    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token)
    
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Could not validade user."