# nerv

### how to run?

=> start redis server with : $redis-server
=> start the celery worker : `python celery -A core.celery_app worker --loglevel=info`
=> start unicorn : `python3 -m uvicorn api:app --reload`

- make your requests with the cli : python cli.py example.com
or with the curl command 






### to fix?

- `127.0.0.1:52944 - "POST /scan HTTP/1.1" 422 Unprocessable Entity` upon sending a request to scan !
