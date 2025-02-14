from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from core.celery_app import app as celery_app
from core.database import get_db_connection
from celery.result import AsyncResult
import time
import uuid
import sqlite3

app = FastAPI()

@app.post("/scan")
async def submit_scan(request: Request):
    data = await request.json()
    target = data.get("target")
    if not target:
        raise HTTPException(status_code=400, detail="Target is required")
    
    scan_id = str(uuid.uuid4())
    print('Generated scan id:', scan_id)
    
    try:
        # Submit Nmap task
        nmap_task = celery_app.send_task(
            'agents.nmap_agent.run_nmap',
            args=(target, "-sV")
        )
        print(f"Submitted Nmap task: {nmap_task.id}") 
        
        # Store task ID in DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scans (scan_id, task_id, target, tool, status, results) VALUES (?, ?, ?, ?, ?, ?)",
            (scan_id, nmap_task.id, target, "nmap", "pending", None)
        )
        conn.commit()
        conn.close()
        # Wait for the task to complete
        task_result = AsyncResult(nmap_task.id, app=celery_app)
        while not task_result.ready():
            time.sleep(1)  # Sleep for a second before checking again
        
        # Get the result of the task
        result = task_result.get()
        
        # Update the database with the result
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE scans SET status = ?, results = ? WHERE task_id = ?",
            ("completed", str(result), nmap_task.id)
        )
        conn.commit()
        conn.close()
        
        return {"scan_id": scan_id, "status": "completed", "results": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit scan: {str(e)}")

@app.get("/results/{scan_id}")
async def get_results(scan_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,))
        scan = cursor.fetchone()
        conn.close()
        
        if scan is None:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Convert row to dictionary
        columns = [desc[0] for desc in cursor.description]
        scan_data = dict(zip(columns, scan))
        
        return JSONResponse(content=scan_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scan results: {str(e)}")
