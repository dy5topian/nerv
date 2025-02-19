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
+ for that database storage , each scan has the following fields:
    - scan_id INTEGER PRIMARY KEY AUTOINCREMENT, # each submitted scan has to have a uniq ID
     - task_id TEXT, task Id , # this is a subtask for each scan there's multiple tools running , thus each one has to have it's own id  
    - target TEXT, # the domain or the ip
    - tool TEXT, # the tool aka the agent
    - status TEXT, # the scan status (pending, complete, ongoing..)
    -  results TEXT (the output of the agent/tool)

### to fix?

- there should be a way to simplify this more maybe?
- so nmap agent look like working , one issue is that i need to store the result of celery in the result field in the database! [done]
- i need to figure out a way to parge each tool output and store it in a way the is easly accessable and easy to output for the user.
- find what to put for the user while the scan is ongoing(output each finshed task or wait till everything is finished)[SEMI-DONE]
- find a way to run everything with one command instead of 4 open teminal sessions
- Ids in uuid4() maybe just make it simple and incremental? this also would avoid collusion?[DONE]
- 

## ideas?
- agents to add: `whatweb`, `gobuster`,`subfinder`,`waymore`.
- maybe a minimalistic web UI.?
- 




