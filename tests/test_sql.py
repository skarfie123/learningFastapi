from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from learning_fastapi.main import app
from learning_fastapi.routers.sql import DBUser, SessionLocal

client = TestClient(app)


def clean_db(session: Session):
    session.query(DBUser).delete()
    session.commit()
    assert session.query(DBUser).count() == 0


def test_create_user():
    session = SessionLocal()
    clean_db(session)
    response = client.post(
        "/sql/users/", json={"email": "test@test.com", "password": "test"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@test.com",
        "is_active": True,
        "items": [],
    }
    user = session.query(DBUser).one()
    assert user.id == 1
    assert user.email == "test@test.com"
    assert user.is_active is True
    assert user.items == []
