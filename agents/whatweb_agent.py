from celery import shared_task
import subprocess
import requests
from core.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='agents.whatweb_agent.run_whatweb')
def run_whatweb(self, target, callback_url=None):
    """
    Run a WhatWeb scan on the specified target.

    :param self: Celery task instance
    :param target: The target to scan.
    :param callback_url: A webhook URL to send results when the scan is completed.
    :return: A dictionary with the scan results.
    """
    logger.info(f"Starting WhatWeb scan for target: {target}")
    
    # Sanitize input to prevent command injection
    target = target.replace(";", "").replace("&", "").replace("|", "").replace("$", "")
    cmd = f"whatweb {target} --log-json=-"
    logger.info(f"Running WhatWeb command: {cmd}")

    try:
        # Execute the WhatWeb command
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=180,
            check=True
        )

        # Parse the JSON output (WhatWeb outputs one JSON object per line)
        import json
        scan_data = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    scan_data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        scan_result = {
            "status": "success",
            "target": target,
            "results": scan_data
        }

        # Store results in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE scans SET status = ?, results = ? WHERE task_id = ?",
            ("complete", str(scan_result), self.request.id)
        )
        conn.commit()
        conn.close()

        logger.info(f"WhatWeb scan completed for target: {target}")
        return scan_result

    except subprocess.CalledProcessError as e:
        error_message = f"Error executing WhatWeb: {e.stderr}"
    except Exception as e:
        error_message = str(e)

    logger.error(f"WhatWeb scan failed for target {target}: {error_message}")

    # Update database with error
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE scans SET status = ?, results = ? WHERE task_id = ?",
        ("failed", error_message, self.request.id)
    )
    conn.commit()
    conn.close()

    return {"status": "error", "message": error_message}
