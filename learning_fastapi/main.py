import time
from typing import Annotated, Awaitable, Callable

from fastapi import Cookie, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from learning_fastapi.routers import (
    background_tasks,
    dependencies,
    examples,
    forms_and_files,
    items_fake_db,
    params,
    request_body,
    response_models,
    security,
    sql,
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


app.include_router(items_fake_db.router)

app.include_router(dependencies.router)

app.include_router(security.router)


@app.middleware("http")
async def add_process_time_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# allow frontends hosted on specified "origins" to call this backend
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # allow cookies and other credentials
    allow_methods=["*"],  # allow all methods, eg PUT, POST
    allow_headers=["*"],  # allow all headers
)

app.include_router(sql.router)

app.include_router(background_tasks.router)
