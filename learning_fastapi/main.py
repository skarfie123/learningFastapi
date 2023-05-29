from enum import Enum
from typing import Annotated, Union

from fastapi import Body, FastAPI, Path, Query
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(
    item_id: str,
    q: str | None = None,
    short: bool = False,
    # validate the string when provided
    q_2: Annotated[
        str | None, Query(min_length=3, max_length=50, regex=r"^\d+query$")
    ] = None,
    # for an array, the annotation is necessary
    # now you can provide multiple values: ?q_list=1&q_list=2
    q_list: Annotated[list[str] | None, Query()] = None,
    q_doc: Annotated[
        list[str] | None,
        Query(
            alias="item-query",  # this useful for example because python names cannot have `-`
            title="Query Param Title",
            description="Query Param Description",
            deprecated=True,
        ),
    ] = None,
):
    item = {"item_id": item_id, "q": q, "q_2": q_2, "q_list": q_list, "q_doc": q_doc}

    # short parsed as True if given [true, True, 1, on, yes], case insensitive
    if not short:
        item.update({"description": "a long description"})
    return item


# Path also has all the metadata that Query has
@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    size: Annotated[float, Query(gt=0, lt=10.5)],
):
    results = {"item_id": item_id, "size": size}
    return results


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
    is_offer: Union[bool, None] = None
    tags: set[str] = set()
    images: list[Image] | None = None


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


class User(BaseModel):
    username: str
    full_name: str | None = None


@app.put("/multi_body")
async def multi_body(
    item: Item,
    user: User,
    # Use Body to add more top level fields to tho body
    importance: Annotated[int, Body(gt=0)],
):
    # if multiple params are models, then they will be nested to form the body
    results = {"item": item, "user": user, "importance": importance}
    return results


class ModelName(str, Enum):  # str is needed for docs
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")  # allow paths with `/` with `:path`
async def read_file(file_path: str):
    return {"file_path": file_path}


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    # arbitrarily deep nesting
    items: list[Item]


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@app.post("/images/multiple/")
# top level of body doesn't have to be a model
async def create_multiple_images(images: list[Image]):
    return images


@app.post("/index-weights/")
# dicts can still be used for the body
async def create_index_weights(weights: dict[int, float], blob: dict):
    return weights, blob


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


@app.post("/items")
async def upload_items(item_id: int, item_1: Item1, item_2: Item2):
    results = {"item_id": item_id, "item_1": item_1, "item_2": item_2}
    return results


@app.post("/item3")
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


@app.post("/item4")
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


# more types
# - https://fastapi.tiangolo.com/tutorial/extra-data-types/#other-data-types
# - https://docs.pydantic.dev/latest/usage/types/#pydantic-types
# - https://docs.pydantic.dev/latest/usage/types/#custom-data-types
