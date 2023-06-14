from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException

router = APIRouter(
    prefix="/dependencies",
    tags=["dependencies"],
    # dependencies can also be passed to the router to affect all endpoints
    # you also do it for the whole app the same way on the main FastAPI instance
    dependencies=[],
)


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


# dependecies can depend on other dependecies, generating a dependency tree


def query_extractor(q: str | None = None):
    return q


def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],
    last_query: Annotated[str | None, Cookie()] = None,
):
    if not q:
        return last_query
    return q


@router.get("/items_query/")
async def read_query(
    query_or_default: Annotated[str, Depends(query_or_cookie_extractor)]
):
    return {"q_or_cookie": query_or_default}


def get_value():
    pass


# dependencies are cached by default, unless use_cache=False is passed to the Depends() decorator
# the cache means that if a dependency is depended on by multiple dependencies of a endpoint, it will only be called once
@router.get("/needy_dependency/")
async def needy_dependency(
    fresh_value: Annotated[str, Depends(get_value, use_cache=False)]
):
    return {"fresh_value": fresh_value}


async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


# for dependencies that need to be run but don't return or you don't need a value from, pass in to the decorator
@router.get("/items_token/", dependencies=[Depends(verify_token)])
async def read_items_token():
    return [{"item": "Foo"}, {"item": "Bar"}]


# you can also use dependencies with yield to do cleanup tasks after the request is finished
async def get_db():
    db = "DBSession()"
    try:
        yield db
    finally:
        # db.close()
        pass


def get_file():
    with open("./somefile.txt") as f:
        yield f
