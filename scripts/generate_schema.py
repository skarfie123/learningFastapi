import json

from fastapi.openapi.utils import get_openapi

from learning_fastapi.main import app

# see https://github.com/tiangolo/fastapi/issues/1173

with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(
        get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
        ),
        f,
    )
