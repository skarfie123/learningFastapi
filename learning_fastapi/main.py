from enum import Enum
from typing import Annotated, Any, Union

from fastapi import (
    Body,
    Cookie,
    FastAPI,
    File,
    Form,
    Header,
    Path,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel, EmailStr, Field, HttpUrl

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/item/{item_id}")
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


@app.get("/image/{image_id}")
async def get_image(image_id: int) -> Image:
    print("getting image", image_id)
    return Image(url=HttpUrl("http://image.jpg", scheme="http"), name="Future Scam")


@app.get("/image2/{image_id}")
async def get_image2(image_id: int) -> Image:
    print("getting image", image_id)
    return dict(  # dict also works
        url=HttpUrl("http://image.jpg", scheme="http"),
        name="Future Scam",
        secret="password",  # attributes not in the return type are filtered out
    )


class InternalImage(Image):
    secret: str


@app.get("/image3/{image_id}")
async def get_image3(image_id: int) -> Image:
    print("getting image", image_id)
    return InternalImage(
        url=HttpUrl("http://image.jpg", scheme="http"),
        name="Future Scam",
        secret="password",  # attributes not in the return type are filtered out
    )


@app.post("/image/{image_id}")
async def upload_image(
    image_id: int, image: Image
) -> int:  # TODO response schema title?
    print("saving image", image)
    return image_id


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr  # requires pydantic[email]
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


# specify response_model if you need to please the type checker
@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    # if we marked the return type as UserOut, mypy would probably complain that we are returning a UserIn.
    # hence we specify Any and the response_model instead
    return user  # password is not defined in output model so it will be dropped


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn2(BaseUser):
    password: str


# alternatively, you can use inheritance, and only the parent fields will be returned
@app.post("/user2/")
async def create_user2(user: UserIn2) -> BaseUser:
    return user


@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})


@app.get("/item2", response_model=Item, response_model_exclude_unset=True)
async def read_item2():
    # by default, this would be converted to an Item and return all the default values,
    # eg description = None
    # but using response_model_exclude_unset=True, only the values actually set will be returned
    # you can also use
    # - response_model_exclude_defaults=True
    # - response_model_exclude_none=True
    # - response_model_exclude
    # - response_model_include
    return {"name": "Foo", "price": 50.2}


# provide the default status code with one of
# - int
# - fastapi.status
# - http.HTTPStatus
@app.post("/item", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}


# Oauth2 for example requires fields pass in as form fields, rather than a json body
# requires python-multipart
@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


# files are uploaded using form data so also require python-multipart
# with File, the whole file will be read as bytes into memory
# suitable for small files
@app.post("/files/")
async def create_file(file: Annotated[bytes, File(description="A file read as bytes")]):
    return {"file_size": len(file)}


# UploadFile uses a spooled file, which stores a limited amount in memory and the rest on disk
@app.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile,
):  # can also do Annotated[UploadFile, File(...)]
    return {"filename": file.filename}


@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/uploadfiles")
async def main():
    content = """
<body>
<form action="/uploadfile/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
