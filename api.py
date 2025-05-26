from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from core.celery_app import app as celery_app
from core.database import get_db_connection
from celery.result import AsyncResult
from utils import utils
from utils.orchestrator import Orchestrator
from typing import List, Dict, Any

app = FastAPI(title="Security Scanner API")

class ScanResponse:
    def __init__(self, scan_id: str, status: str, results: List[Dict[str, Any]] = None):
        self.scan_id = scan_id
        self.status = status
        self.results = results or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scan_id": self.scan_id,
            "status": self.status,
            "results": self.results
        }

@app.post("/scan")
async def submit_scan(request: Request):
    data = await request.json()
    target = data.get("target")
    if not target:
        raise HTTPException(status_code=400, detail="Target is required")

    # Get a new scan_id (simulate what orchestrator would do)
    orchestrator = Orchestrator(target)
    scan_id = orchestrator._initialize_scan()

    # Submit the orchestrator as a background Celery task
    celery_app.send_task("utils.orchestrator.orchestrate_full_scan", args=[target])

    # Return immediately
    return JSONResponse(content={
        "status": "submitted",
        "scan_id": scan_id,
        "message": "Scan has been submitted and is processing in the background."
    })

@app.get("/results/{scan_id}", response_model=Dict[str, Any])
async def get_results(scan_id: int) -> JSONResponse:
    """
    Retrieve results for a specific scan ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all scans for the given scan_id
        cursor.execute(
            "SELECT scan_id, task_id, tool, status, results FROM scans WHERE scan_id = ?",
            (scan_id,)
        )
        scans = cursor.fetchall()
        conn.close()
        
        if not scans:
            raise HTTPException(status_code=404, detail=f"Scan with ID {scan_id} not found")
        
        # Process scan results
        results = []
        for scan in scans:
            scan_id, task_id, tool, status, result = scan
            results.append({
                "task_id": task_id,
                "tool": tool,
                "status": status,
                "results": result
            })
        
        response = ScanResponse(
            scan_id=scan_id,
            status="completed" if all(r["status"] == "complete" for r in results) else "in-progress",
            results=results
        )
        
        return JSONResponse(content=response.to_dict())
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scan results: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)