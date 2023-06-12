from typing import Annotated

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field

router = APIRouter()

# schema examples
# - item_1: pydantic schema_extra https://docs.pydantic.dev/latest/usage/schema/#schema-customization
# - item_2: pydantic field example
# - item_3: fastapi Body example (only works for single body)
# - item_4: fastapi Body examples (only works for single body)


class Item0(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class Item1(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


class Item2(BaseModel):
    name: str = Field(example="Foo")
    description: str | None = Field(default=None, example="A very nice Item")
    price: float = Field(example=35.4)
    tax: float | None = Field(default=None, example=3.2)


@router.post("/items")
async def upload_items(item_id: int, item_1: Item1, item_2: Item2):
    results = {"item_id": item_id, "item_1": item_1, "item_2": item_2}
    return results


@router.post("/item3")
async def upload_item3(
    item_id: int,
    item_3: Annotated[
        Item0,
        Body(
            example={
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            },
        ),
    ],
):
    results = {"item_id": item_id, "item_3": item_3}
    return results


@router.post("/item4")
async def upload_item4(
    item_id: int,
    item_4: Annotated[
        Item0,
        Body(
            examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
):
    results = {"item_id": item_id, "item_4": item_4}
    return results
