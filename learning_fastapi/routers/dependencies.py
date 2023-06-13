from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends

router = APIRouter(prefix="/dependencies", tags=["dependencies"])


# the function parameters are used as query parameters in every endpoint that depends on this function
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


CommonsDep = Annotated[dict, Depends(common_parameters)]


@router.get("/items/")
async def read_items(commons: CommonsDep):
    return commons


@router.get("/users/")
async def read_users(commons: CommonsDep):
    return commons


# async vs sync: endpoint and dependencies are independent of each other


# with multiple dependencies, the parameters will be the union set of the dependencies'
async def common_parameters2(q: str | None = None, name: str = "test"):
    return {"q": q, "name": name}


@router.get("/items_union/")
async def read_items_union(
    commons: CommonsDep, common2: Annotated[dict, Depends(common_parameters2)]
):
    return commons, common2


# classes can also be used as dependencies, or any callable
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@router.get("/items_class/")
async def read_items_class(
    commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]
):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]  # noqa: E203
    response.update({"items": items})
    return response


@dataclass
class CommonQueryParamsDC:
    q: str | None = None
    skip: int = 0
    limit: int = 100


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# it also works for dataclasses
@router.get("/items_dataclass/")
async def read_items_dataclass(
    commons: Annotated[
        CommonQueryParamsDC, Depends()
    ]  # for classes you can omit the Depends arg and the main type hint will be used
):
    return commons
