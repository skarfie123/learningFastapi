from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import HTMLResponse

router = APIRouter()


# Oauth2 for example requires fields pass in as form fields, rather than a json body
# requires python-multipart
@router.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


# files are uploaded using form data so also require python-multipart
# with File, the whole file will be read as bytes into memory
# suitable for small files
@router.post("/files/")
async def create_file(file: Annotated[bytes, File(description="A file read as bytes")]):
    return {"file_size": len(file)}


# UploadFile uses a spooled file, which stores a limited amount in memory and the rest on disk
@router.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile,
):  # can also do Annotated[UploadFile, File(...)]
    return {"filename": file.filename}


@router.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@router.get("/uploadfiles")
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
