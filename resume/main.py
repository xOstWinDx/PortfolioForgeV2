# main.py
import argparse
import logging

from fastapi import FastAPI

from src.presentation.http.router import router
from src.presentation.broker.rabbit.consumer import start_consumer

app = FastAPI(
    title="Resume API",
    version="0.0.1",
    description="АПИ для резюме - визитки.",
    openapi_tags=[
        {
            "name": "Profile",
            "description": "Endpoints для получения данных визитки.",
        },
        {
            "name": "Projects",
            "description": "Endpoints для получения информации о проектах, в которых я участвовал.",
        },
    ],
)
app.include_router(router)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer", action="store_true", help="Run RabbitMQ consumer")
    args = parser.parse_args()

    if args.consumer:
        start_consumer()  # Асинхронный запуск консьюмера
    else:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
