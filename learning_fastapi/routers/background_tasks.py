from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

router = APIRouter(prefix="/background-tasks", tags=["background-tasks"])


# the background task will be executed after the request is finished
def send_email(email: str, message=""):
    print(f"Sending {message} to {email}")


@router.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, message="some notification")
    return {"message": "Notification sent in the background"}


# background tasks can also be added in dependencies. they'll be collected together and all
# performed after the request
def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        message = f"found query: {q}\n"
        background_tasks.add_task(print, message)
    return q


@router.post("/send-notification2/{email}")
async def send_notification2(
    email: str, background_tasks: BackgroundTasks, q: Annotated[str, Depends(get_query)]
):
    message = f"message to {email}\n"
    background_tasks.add_task(print, message)
    return {"message": "Message sent", "query": q}
