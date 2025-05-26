from celery import shared_task
import subprocess
import xml.etree.ElementTree as ET
import requests
from core.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='agents.nmap_agent.run_nmap')
def run_nmap(self, target, callback_url=None):
    """
    Run an Nmap scan on the specified target with the given options.

    :param self: Celery task instance
    :param target: The target to scan.
    :param options: The Nmap options to use.
    :param callback_url: A webhook URL to send results when the scan is completed.
    :return: A dictionary with the scan results.
    """
    logger.info(f"Starting nmap scan for target: {target}")
    
    # Sanitize input to prevent command injection
    target = target.replace(";", "").replace("&", "").replace("|", "").replace("$", "")
    cmd = f"nmap -F {target} -oX -"
    logger.info(f"Running nmap command: {cmd}")
    
    try:
        # Execute the Nmap command
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=300,
            check=True
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

        # Store results in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE scans SET status = ?, results = ? WHERE task_id = ?",
            ("complete", str(scan_result), self.request.id)
        )
        conn.commit()
        conn.close()

        logger.info(f"Nmap scan completed for target: {target}")
        return scan_result

    except subprocess.CalledProcessError as e:
        error_message = f"Error executing Nmap: {e.stderr}"
    except ET.ParseError as e:
        error_message = f"XML Parsing error: {e}"
    except Exception as e:
        error_message = str(e)

    logger.error(f"Nmap scan failed for target {target}: {error_message}")

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

def get_nmap_ports(scan_result):
    """
    Extracts and returns a list of open port numbers from the nmap scan result.
    :param scan_result: The dictionary returned by run_nmap
    :return: List of open port numbers (as integers)
    """
    ports = scan_result.get("ports", [])
    return [int(port_info["port"]) for port_info in ports if "port" in port_info]

