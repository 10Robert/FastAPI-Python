from .utils import *
from fastapi import status
from ..database import get_db
from ..utils.crud import get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = overreide_get_user

def test_read_user(test_user):
    response = client.get("user")
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == "Robert"
    assert response.json()['email'] == "robertlucasmtz124@gmail.com"
    assert response.json()['first_name'] == "Robert"
    assert response.json()['role'] == "Admin"
    assert response.json()['phone_number'] == "39366856"
    assert response.json()['is_active'] == True
    assert response.json()['last_name'] == "Azevedo"

def test_chage_password_success(test_user):
    response = client.patch("user/password", json={"password": "test_123", "new_password": "test_12345"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
