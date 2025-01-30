
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import pytest
from fastapi.testclient import TestClient
from ..main import app
from sqlalchemy.orm import sessionmaker
from ..database import Base
from sqlalchemy import text
from ..models import Todos, Users
from ..utils.crud import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def overreide_get_user():
    return {"username": "Robert", "id": 1, "role": "admin"}

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title = "learn to code!",
        description = "Need to learn everday!",
        priority = 5,
        complete = False,
        owner_id = 1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    user = Users(
        id = 1,
        email = "robertlucasmtz124@gmail.com",
        username = "Robert",
        first_name = "Robert",
        last_name = "Azevedo",
        hashed_password = bcrypt_context.hash("test_123"),
        is_active = True,
        role = "Admin",
        phone_number = "39366856"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()