from fastapi import FastAPI, HTTPException
from core.celery_app import app as celery_app
from core.database import get_db_connection
import uuid
# Define a Pydantic model for the request body

app = FastAPI()

@app.post("/scan")
async def submit_scan():
    target = scan_request.target  # Extract the target from the request body
    scan_id = str(uuid.uuid4())
    # Submit Nmap task
    nmap_task = celery_app.send_task(
        'agents.nmap_agent.run_nmap',
        args=(target, "-sV")
    )
    
    # Submit WhatWeb task
    whatweb_task = celery_app.send_task(
        'agents.whatweb_agent.run_whatweb',
        args=(target,)
    )
    
    # Store task IDs in DB
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO scans (id, target, tool, status) VALUES (?, ?, ?, ?)",
        (scan_id, target, "nmap", "pending")
    )
    conn.commit()
    conn.close()
    
    return {"scan_id": scan_id}

@app.get("/results/{scan_id}")
async def get_results(scan_id: str):
    conn = get_db_connection()
    scan = conn.execute(
        "SELECT * FROM scans WHERE id = ?", (scan_id,)
    ).fetchone()
    conn.close()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return dict(scan)
