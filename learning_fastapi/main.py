from typing import Annotated

from fastapi import Cookie, FastAPI, Header, HTTPException, Request, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse

from learning_fastapi.routers import (
    dependencies,
    examples,
    forms_and_files,
    items_db,
    params,
    request_body,
    response_models,
)

app = FastAPI(
    # override the response for validation errors based on our custom handler
    # https://github.com/tiangolo/fastapi/discussions/8298#discussioncomment-5150722
    responses={422: {"model": str}},
)


@app.get("/", deprecated=True)
def read_root():
    """
    This is a fastapi endpoint:

    - **Hello**: world
    """
    return {"Hello": "World"}


app.include_router(params.router)


app.include_router(request_body.router)


app.include_router(examples.router)


# more types
# - https://fastapi.tiangolo.com/tutorial/extra-data-types/#other-data-types
# - https://docs.pydantic.dev/latest/usage/types/#pydantic-types
# - https://docs.pydantic.dev/latest/usage/types/#custom-data-types


@app.get("/headers")
async def headers(
    cookie: Annotated[str, Cookie()],
    some_number: Annotated[int, Header()],
    more_numbers: Annotated[list[int] | None, Header()] = None,
):
    # Headers are case insensitive, and by convention use hyphens not underscores
    # Cookies are just a special header:
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cookie
    return {"cookie": cookie, "Some-Number": some_number, "more_numbers": more_numbers}


app.include_router(response_models.router)


# provide the default status code with one of
# - int
# - fastapi.status
# - http.HTTPStatus
@app.post("/item", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}


app.include_router(forms_and_files.router)


@app.get("/error")
async def error():
    raise HTTPException(status_code=404, detail="Not found")


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


# override a built in handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if None:
        # you can reuse the default handler
        return await request_validation_exception_handler(request, exc)
    return PlainTextResponse(str(exc), status_code=400)


app.include_router(items_db.router)

app.include_router(dependencies.router)
