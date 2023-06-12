from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Path, Query

from learning_fastapi.tags import Tags

router = APIRouter()


@router.get("/item/{item_id}", tags=[Tags.items])
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
@router.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    size: Annotated[float, Query(gt=0, lt=10.5)],
):
    results = {"item_id": item_id, "size": size}
    return results


class ModelName(str, Enum):  # str is needed for docs
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@router.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


@router.get("/files/{file_path:path}")  # allow paths with `/` with `:path`
async def read_file(file_path: str):
    return {"file_path": file_path}
