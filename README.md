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
- remember to get_db_connection before each database query
- 




### to fix?

- `127.0.0.1:52944 - "POST /scan HTTP/1.1" 422 Unprocessable Entity` upon sending a request to scan ! [Done]
- i still don't understand the need for for redis and ! , for celery ? well task distrebutions maybe 
- why can't we just do everyhting by subprocess spawning and not using celery?

- so nmap agent look like working , one issue is that i need to store the result of celery in the result field in the database!



===> i was having this crazy issue that one scan submition, i get empty open ports 
- a bit of context , my vm is slow , so i sshed to it with cursor on windows , but sence bridged is not working am using host-only rendering my kali unable to access the internet
- this is why my nmap yeilds 0 ports cuz it can't resolve any ip/domain. fuck.
