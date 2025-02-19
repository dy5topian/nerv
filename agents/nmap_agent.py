from celery import shared_task
import subprocess
import xml.etree.ElementTree as ET
import requests
from core.database import get_db_connection

@shared_task(bind=True)
def run_nmap(self, target, options="-sV", callback_url=None):
    """
    Run an Nmap scan on the specified target with the given options.

    :param self: Celery task instance (to access task ID).
    :param target: The target to scan.
    :param options: The Nmap options to use.
    :param callback_url: A webhook URL to send results when the scan is completed.
    :return: A dictionary with the scan results.
    """
    # Get the task ID assigned by Celery
    task_id = self.request.id  

    # Sanitize input to prevent command injection
    target = target.replace(";", "").replace("&", "").replace("|", "").replace("$", "")
    cmd = f"nmap {options} {target} -oX -"
    
    try:
        # Execute the Nmap command
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=300,
            check=True  # Ensure subprocess raises an error on failure
        )

        # Parse the XML output
        root = ET.fromstring(result.stdout)
        ports = []
        for port in root.findall(".//port"):
            ports.append({
                "port": port.attrib['portid'],
                "service": port.find('service').attrib.get('name', 'unknown')
            })

        # Prepare result data
        scan_result = {
            "status": "success",
            "target": target,
            "ports": ports
        }

        # Store results in the database using TASK ID
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE scans SET status = ?, results = ? WHERE task_id = ?",
            ("completed", str(scan_result), task_id)
        )
        conn.commit()
        conn.close()

        # Send result to webhook if provided
        if callback_url:
            try:
                requests.post(callback_url, json={"task_id": task_id, "results": scan_result})
            except requests.RequestException as e:
                print(f"[!] Failed to send results to webhook: {e}")

        return scan_result

    except subprocess.CalledProcessError as e:
        error_message = f"Error executing Nmap: {e.stderr}"
    except ET.ParseError as e:
        error_message = f"XML Parsing error: {e}"
    except Exception as e:
        error_message = str(e)

    # Update database with error using TASK ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE scans SET status = ?, results = ? WHERE task_id = ?",
        ("failed", error_message, task_id)
    )
    conn.commit()
    conn.close()

    return {"status": "error", "message": error_message}

