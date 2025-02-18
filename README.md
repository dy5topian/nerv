# nerv
![eva](https://github.com/user-attachments/assets/5336736d-c0ba-40ff-955d-e0acbd50fcfb)


# what's that ?
- nerv is a cli tool that aims to automate the basic hardship of enumeration & recon that takes a loot of time during each pentesting or bug bounty engagement.

# how to run?
!note: each of these commands should be run in a seprate terminal session.</br>
  => start redis server with : `redis-server`. </br>
  => start the  celery worker : `python3 celery -A core.celery_app worker --loglevel=info`. </br>
  => start unicorn : `python3 -m uvicorn api:app --reload`.</br>
  => make your requests with the cli :` python cli.py example.com` </br>

### archetecure?
+  redis works like a broker that stores tmp data of the tasks distrebuted to agents
+ celery is needed to create and distribute task to agents , each agent is a subprocess of a tool , once the scan is done by the tool it reports back reports back to redis  ,and redis notifies celery which in it's tourn stores the data in a local databases fo future consultation


### to fix?

- there should be a way to simplify this more maybe?
- so nmap agent look like working , one issue is that i need to store the result of celery in the result field in the database! [done]
- 



===> i was having this crazy issue that on scan submission, i get empty open ports 
- a bit of context , my vm is slow , so i sshed to it with cursor on windows , but sence bridged is not working am using host-only rendering my kali unable to access the internet
- this is why my nmap yeilds 0 ports cuz it can't resolve any ip/domain. fuck.

# .gitignore:
- for each agent , you need to declare it as '@shared_task' in it's main function then celery will have access to it.
- remember to get_db_connection before each database query
