#!/bin/sh

exec su - postgres; postgres -c max_connections=100 -c shared_buffers=1GB -c effective_cache_size=4GB -c idle_in_transaction_session_timeout=10s -D /opt/app/data
