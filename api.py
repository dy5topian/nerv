from fastapi import FastAPI, HTTPException, Request
from core.celery_app import app as celery_app
from core.database import get_db_connection
import uuid
# Define a Pydantic model for the request body

app = FastAPI()

@app.post("/scan")
async def submit_scan(request: Request):
    data = await request.json()
    target = data.get("target")
    if not target:
        raise HTTPException(status_code=400, detail="Target is required")
    scan_id = str(uuid.uuid4())
    
    try:
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
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO scans (id, target, tool, status) VALUES (?, ?, ?, ?)",
                (scan_id, target, "nmap", "pending")
            )
            conn.execute(
                "INSERT INTO scans (id, target, tool, status) VALUES (?, ?, ?, ?)",
                (scan_id, target, "whatweb", "pending")
            )
            conn.commit()
        
        return {"scan_id": scan_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit scan: {e}")

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
