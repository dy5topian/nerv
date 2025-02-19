from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from core.celery_app import app as celery_app
from core.database import get_db_connection
from celery.result import AsyncResult
import time
import uuid
import sqlite3

app = FastAPI()

AGENTS = [{"task": "agents.nmap_agent.run_nmap","tool":"nmap","args": ["-sV"]}]

@app.post("/scan")
async def submit_scan(request: Request):
    data = await request.json()
    target = data.get("target")
    if not target:
        raise HTTPException(status_code=400, detail="Target is required")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    
    # keep track of the tasks IDs
        task_ids = []
        
        # loop through agents -> may need a better logic and orchestration.
        for agent in AGENTS:
            task = celery_app.send_task(agent["task"], args=(target, *agent["args"]))
            task_ids.append(task.id)
                
            cursor.execute("INSERT INTO scans (task_id, target, tool, status, results) VALUES (?, ?, ?, ?, ?)",(task.id, target, agent["tool"], "pending", None))
            scan_id = cursor.lastrowid
            print(f"Assigned scan id: {scan_id}")
            conn.commit()
            conn.close()

            return {"scan_id": scan_id, "status": "in_progress", "tasks": task_ids}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit scan: {str(e)}")

@app.get("/results/{scan_id}")
async def get_results(scan_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT scan_id,task_id,tool, status, results FROM scans WHERE scan_id = ?", (scan_id,))
        scans = cursor.fetchall()
        conn.close()
        
        if not scans:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        results = []
        for scan in scans:
            scan_id,task_id,tool, status, result = scan
            results.append({"task_id":task_id,"tool": tool, "status": status, "results": result})
        
        return JSONResponse(content={"scan_id": scan_id,"results": results})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scan results: {str(e)}")

