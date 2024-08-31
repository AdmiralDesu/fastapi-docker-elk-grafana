from uvicorn import run
from config import config

print(config.api_info.host)
print(config.api_info.port)

if __name__ == '__main__':
    run(
        "main:app",
        host="127.0.0.1",
        port=config.api_info.port,
    )

