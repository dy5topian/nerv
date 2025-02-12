# nerv

![nerv](![image](https://github.com/user-attachments/assets/bebd9448-6ab5-4541-8db6-38ba8b740320)
)

### how to run?

=> start redis server with : $redis-server
=> start the celery worker : `python celery -A core.celery_app worker --loglevel=info`
=> start unicorn : `python3 -m uvicorn api:app --reload`

- make your requests with the cli : python cli.py example.com
or with the curl command
- for each agent , you need to declare it as '@shared_task' in it's main function then celery will have access to it.
- the command line errors 500 , but celery still executes the nmap agent in the background , need some sort of a session request  unitl it gets back the data!






### to fix?

- `127.0.0.1:52944 - "POST /scan HTTP/1.1" 422 Unprocessable Entity` upon sending a request to scan ! [Done]
- c
