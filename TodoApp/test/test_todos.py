from sqlalchemy.orm.session import Session
from starlette import status
from TodoApp.utils.crud import get_current_user
from ..models import Todos
from .utils import *
from ..database import get_db
from ..main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = overreide_get_user

def test_read_all_authenticated(test_todo) -> None:
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"complete": False, "title": "learn to code!", "description": "Need to learn everday!",
                                "priority": 5, "id": 1, "owner_id": 1}]
   
def test_read_one_authenticated(test_todo) -> None:
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK

def test_read_one_authenticated_not_found(test_todo) -> None:
    response = client.get("/todo/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}

def test_create_todo(test_todo) -> None:
    request_data = {
        "title": "New Todo",
        "description": "New todo description",
        "priority": 5,
        "complete": False
    }
    response = client.post("/todo", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    db: Session = TestingSessionLocal()
    model: Todos | None = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title  == request_data.get("title") #type: ignore
    assert model.description == request_data.get("description") #type: ignore
    assert model.priority == request_data.get("priority") #type: ignore
    assert model.complete == request_data.get("complete") #type: ignore
    
def test_update_todo(test_todo) -> None:
    request_data = {
        "title": "Change the title of the todo already saved!!",
        "description": "Need to learn everday!",
        "priority": 5,
        "complete": False
    }

    response = client.put("/todo/1", json=request_data)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db: Session = TestingSessionLocal()
    model: Todos | None = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title  == request_data.get("title") #type: ignore
    assert model.description == request_data.get("description") #type: ignore
    assert model.priority == request_data.get("priority") #type: ignore
    assert model.complete == request_data.get("complete") #type: ignore



def test_update_todo_not_found(test_todo) -> None:
    request_data = {
        "title": "New Todo",
        "description": "New todo description",
        "priority": 5,
        "complete": False
    }
    response = client.put("/todo/2", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}

def test_delete_todo(test_todo) -> None:
    response = client.delete("/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None and client.get("/todo/1").status_code == status.HTTP_404_NOT_FOUND  


def test_delete_todo_not_found(test_todo) -> None:
    response = client.delete("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}

