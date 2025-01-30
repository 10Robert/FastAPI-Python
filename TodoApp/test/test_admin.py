from ..utils.crud import get_current_user
from .utils import *
from ..database import get_db
from fastapi import status
from sqlalchemy.orm import Session

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = overreide_get_user

def test_admin_read_all_authenticated(test_todo):
    response =  client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'id': 1, 'priority': 5, 'owner_id': 1, 'complete': False, 
                                'description': 'Need to learn everday!', 'title': 'learn to code!'}]

def test_admin_delete_todo(test_todo) -> None:
    response = client.delete("/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db: Session = TestingSessionLocal()
    model = db.query(Todos.id == 1).first()
    assert model is None
    
def test_delete_todo_not_found(test_todo):
    response = client.delete("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found."}