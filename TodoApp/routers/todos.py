from fastapi import APIRouter, HTTPException, Path
from starlette import status
from ..models import Todos
from ..database import db_dependency
from ..utils.crud import user_dependency
from ..schemas.schema import TodoRequest

router = APIRouter()



@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todo_user(user: user_dependency, db: db_dependency):
    if user is None:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, 
                    todo_id:int = Path(gt=0)):
    if user is None:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency, db: db_dependency, 
                      todo_request: TodoRequest):
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0),):
    if user is None:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
 
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
  
    todo_model.title = todo_request.title # type: ignore
    todo_model.description = todo_request.description # type: ignore
    todo_model.complete = todo_request.complete # type: ignore
    todo_model.priority = todo_request.priority # type: ignore
    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency,
                      todo_id: int = Path(gt=0)):
        if user is None:
            HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail="Todo not found.")
        
        db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
        db.commit()
