from typing import Any

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr, Field, HttpUrl

from learning_fastapi.tags import Tags

router = APIRouter()


class Image(BaseModel):
    url: HttpUrl
    name: str


@router.get("/image/{image_id}")
async def get_image(image_id: int) -> Image:
    print("getting image", image_id)
    return Image(url=HttpUrl("http://image.jpg", scheme="http"), name="Future Scam")


@router.get("/image2/{image_id}")
async def get_image2(image_id: int) -> Image:
    print("getting image", image_id)
    return dict(  # dict also works
        url=HttpUrl("http://image.jpg", scheme="http"),
        name="Future Scam",
        secret="password",  # attributes not in the return type are filtered out
    )


class InternalImage(Image):
    secret: str


@router.get("/image3/{image_id}")
async def get_image3(image_id: int) -> Image:
    print("getting image", image_id)
    return InternalImage(
        url=HttpUrl("http://image.jpg", scheme="http"),
        name="Future Scam",
        secret="password",  # attributes not in the return type are filtered out
    )


@router.post("/image/{image_id}")
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
@router.post("/user/", response_model=UserOut, tags=[Tags.users])
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
@router.post("/user2/")
async def create_user2(user: UserIn2) -> BaseUser:
    return user


@router.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})


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


@router.get("/item2", response_model=Item, response_model_exclude_unset=True)
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
