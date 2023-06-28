from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

router = APIRouter()

# PUT vs PATCH
# - PUT replaces the whole resource
# - PATCH updates the resource, but only the fields you specify


class ItemDB(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []


items_db = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@router.get("/items_db/{item_id}", response_model=ItemDB)
async def read_item_db(item_id: str):
    return items_db[item_id]


@router.put("/items_db/{item_id}", response_model=ItemDB)
async def update_item_db(item_id: str, item: ItemDB):
    # note by this point, item includes all the default values, eg tax = 10.5
    # so when updating the db, the default value will replace the any existing value
    update_item_encoded = jsonable_encoder(item)
    items_db[item_id] = update_item_encoded
    return update_item_encoded


@router.patch("/items_db/{item_id}", response_model=ItemDB)
async def update_item_db2(item_id: str, item: ItemDB):
    stored_item_data = items_db[item_id]
    stored_item_model = ItemDB(**stored_item_data)
    update_data = item.dict(
        exclude_unset=True
    )  # exclude any values that are not set in the update
    updated_item = stored_item_model.copy(update=update_data)
    items_db[item_id] = jsonable_encoder(updated_item)
    return updated_item
