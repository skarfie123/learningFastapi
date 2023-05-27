from enum import Enum
from typing import Annotated, Union

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


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
        str | None, Query(min_length=3, max_length=50, regex="^\d+query$")
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
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


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
