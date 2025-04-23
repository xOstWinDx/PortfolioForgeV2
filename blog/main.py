from fastapi import FastAPI

app = FastAPI(
    title="Blog API",
    version="0.0.1",
    description="Blog API",
    openapi_tags=[
        {
            "name": "Posts",
            "description": "Операции с постами",
        },
        {
            "name": "Comments",
            "description": "Операции с комментариями",
        },
    ],
)


@app.get("/health", status_code=200)
async def root() -> dict[str, str]:
    return {"status": "Ok"}
