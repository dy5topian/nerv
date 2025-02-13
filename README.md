# nerv
![eva](https://github.com/user-attachments/assets/5336736d-c0ba-40ff-955d-e0acbd50fcfb)

### how to run?
```
=> start redis server with : $redis-server
=> start the -m celery worker : `python celery -A core.celery_app worker --loglevel=info`
=> start -m unicorn : `python3 -m uvicorn api:app --reload`

make your requests with the cli : python cli.py example.com or with the curl command

```




- for each agent , you need to declare it as '@shared_task' in it's main function 
then celery will have access to it.
- the command line errors 500 , but celery still executes the nmap agent in the background ,
 need some sort of a session request  unitl it gets back the data!






### to fix?

- `127.0.0.1:52944 - "POST /scan HTTP/1.1" 422 Unprocessable Entity` upon sending a request to scan ! [Done]
- i still don't understand the need for for redis and ! , for celery ? well task distrebutions maybe 
- why can't we just do everyhting by subprocess spawning and not using celery?

