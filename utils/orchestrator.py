import re
import json
from utils import utils
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from core.celery_app import app as celery_app
from core.database import get_db_connection
import time

class Orchestrator:
    def __init__(self, target):
        self.target = target
        self.agents = utils.ag_list()
        print('initiating orchestrator')

    def run(self):
        try:
            scan_id = self._initialize_scan()
            self._start_nmap_scan(scan_id)
            return {"status": "Scan initiated", "scan_id": scan_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to submit scan: {str(e)}")

    def _initialize_scan(self):
        """Initialize a new scan and return its ID"""
        scan_id = utils.get_last_scan_id()
        return (scan_id + 1) if scan_id is not None else 1

    def _start_nmap_scan(self, scan_id):
        """Start the initial nmap scan"""
        nmap_agent = self.agents['nmap']
        return self.execute_task(nmap_agent, scan_id)

    def execute_task(self, agent, scan_id):
        """Execute a specific agent task and record it in the database"""
        task = celery_app.send_task(agent["task"], args=[self.target, agent["args"]])
        self._record_scan_in_db(scan_id, task.id, agent["tool"])
        return task.id

    def _record_scan_in_db(self, scan_id, task_id, tool):
        """Record scan details in the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scans (scan_id, task_id, target, tool, status, results) VALUES (?, ?, ?, ?, ?, ?)",
            (scan_id, task_id, self.target, tool, "in-progress", None)
        )
        conn.commit()
        conn.close()


@celery_app.task(name="utils.orchestrator.orchestrate_full_scan")
def orchestrate_full_scan(target, poll_interval=10):
    """Orchestrate a complete scan process with polling"""
    try:
        orchestrator = Orchestrator(target)
        initial_result = orchestrator.run()
        scan_id = initial_result["scan_id"]

        # Wait for nmap scan to complete
        while utils.get_nmap_status(scan_id) != "complete":
            if utils.get_nmap_status(scan_id) == "failed":
                return {
                    "status": "Nmap scan failed",
                    "scan_id": scan_id
                }
            print('waiting for nmap scan to finish...')
            time.sleep(poll_interval)
        open_ports = utils.get_open_ports(scan_id)
        # Continue with domain scans if applicable
        if not utils.is_domain(target):
            return {
                "status": "Target is an IP. See nmap output or initiate a scan with a domain name",
                "scan_id": scan_id
            }

        # If port 80 or 443 is open, run whatweb
        if 80 in open_ports or 443 in open_ports:
            # Import here to avoid circular import
            from core.celery_app import app as celery_app
            whatweb_task_id = celery_app.send_task('agents.whatweb_agent.run_whatweb', args=[target])
            orchestrator._record_scan_in_db(scan_id, whatweb_task_id.id, "whatweb")
            # Optionally, you can wait for completion or just return the task id
            return {
                "status": "WhatWeb scan started (HTTP/HTTPS port open)",
                "task_id": scan_id,
                "whatweb_task_id": whatweb_task_id.id
            }

        # TODO: Implement domain-specific scans
        return {
            "status": "Domain scans pending implementation", 
            "scan_id": scan_id
        }
    except Exception as e:
        error_msg = f"Failed to orchestrate full scan: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}