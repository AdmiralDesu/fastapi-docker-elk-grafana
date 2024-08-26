#!/bin/sh

exec minio server /opt/app/data --address 0.0.0.0:9000 --console-address 0.0.0.0:9001
