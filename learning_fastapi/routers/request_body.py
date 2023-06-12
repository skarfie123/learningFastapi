from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, HttpUrl

from learning_fastapi.tags import Tags

router = APIRouter()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    price: float
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    is_offer: bool | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


@router.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    # you can use jsonable_encoder convert many types into jsonable equivalents, eg:
    # - datetime -> str (ISO)
    # - pydantic models -> dict
    print(jsonable_encoder(item))
    return {"item_name": item.name, "item_id": item_id}


class User(BaseModel):
    username: str
    full_name: str | None = None


@router.put("/multi_body", tags=[Tags.items, Tags.users])
async def multi_body(
    item: Item,
    user: User,
    # Use Body to add more top level fields to tho body
    importance: Annotated[int, Body(gt=0)],
):
    # if multiple params are models, then they will be nested to form the body
    results = {"item": item, "user": user, "importance": importance}
    return results


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    # arbitrarily deep nesting
    items: list[Item]


@router.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@router.post("/images/multiple/")
# top level of body doesn't have to be a model
async def create_multiple_images(images: list[Image]):
    return images


@router.post("/index-weights/")
# dicts can still be used for the body
async def create_index_weights(weights: dict[int, float], blob: dict):
    return weights, blob
