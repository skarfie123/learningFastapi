from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

# region: database

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # this is specific to sqlite
    # sqlite by default does not allow concurrent connections from multiple threads
    # this is to prevent the same connection being used for different things
    # with fastapi, we will use the dependency injection to ensure each request gets its own connection
    connect_args={"check_same_thread": False},
)

# a sessionmaker is a class that will be used to create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# endregion
# region: models
# https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#orm-declarative-models

indexed_pk = Annotated[int, mapped_column(primary_key=True, index=True)]


class DBUser(Base):
    __tablename__ = "users"

    id: Mapped[indexed_pk]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    # user.items: List[DBItem]
    items: Mapped[List["DBItem"]] = relationship(back_populates="owner")


class DBItem(Base):
    __tablename__ = "items"

    id: Mapped[indexed_pk]
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # item.owner: DBUser
    owner: Mapped[DBUser] = relationship(back_populates="items")


# endregion
# region: schemas


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        # orm mode tells pydantic to convert the sqlalchemy objects to pydantic objects
        # eg. now it will also try `id = item.id` instead of just `id = item.["id"]`
        # https://docs.pydantic.dev/latest/usage/models/#orm-mode-aka-arbitrary-class-instances
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True


# endregion
# region: crud


def get_user(db: Session, user_id: int):
    return db.query(DBUser).filter(DBUser.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(DBUser).filter(DBUser.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[DBUser]:
    return db.query(DBUser).order_by(DBUser.id).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = DBUser(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    # refresh to get any new data from the db, eg. the id
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DBItem).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: ItemCreate, user_id: int):
    db_item = DBItem(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# endregion
# region: main

# create all the tables
# in a real app you should use Alembic instead (which supports migrations)
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/sql", tags=["sql"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# becuase the endpoints specify response models that use orm_mode,
# you can return sqlalchemy objects directly without having to convert them to pydantic objects
# pydantic automatically extracts only the fields you need from the sqlalchemy object
@router.post("/users/", response_model=User)
def create_user_(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)


@router.get("/users/", response_model=list[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/users/{user_id}/items/", response_model=Item)
def create_item_for_user(user_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    return create_user_item(db=db, item=item, user_id=user_id)


@router.get("/items/", response_model=list[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = get_items(db, skip=skip, limit=limit)
    return items


# endregion
