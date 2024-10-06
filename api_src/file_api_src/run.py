from uvicorn import run
from config import config


if __name__ == "__main__":
    run(
        "main:app",
        host=config.api_info.host,
        port=int(config.api_info.port),
        # log_config="./log.ini"
    )
