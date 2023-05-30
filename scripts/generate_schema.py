import json

from learning_fastapi.main import app

# see https://github.com/tiangolo/fastapi/issues/1173

with open("openapi.json", "w", encoding="utf-8") as f:
    json.dump(app.openapi, f)
