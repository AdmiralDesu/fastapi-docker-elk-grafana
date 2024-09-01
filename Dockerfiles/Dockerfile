FROM python:3.12-alphine

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive \
  && apt-get install -y net-tools netcat-traditional curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir --parents /opt/app

WORKDIR /opt/app

COPY dependencies/file_api/requirements.txt .

RUN python -m venv .venv
RUN .venv/bin/pip install --no-cache-dir  -r /opt/app/requirements.txt

COPY ../file_api_src/ /opt/app

COPY ./entrypoints/entrypoint_file_api.sh /opt/app/entrypoint.sh

RUN chmod +x /opt/app/entrypoint.sh





