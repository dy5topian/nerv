import re
from core.database import get_db_connection
import ast
def ag_list():
    return {
        "nmap": {"task": "agents.nmap_agent.run_nmap", "tool": "nmap", "args": ["-sSV -p-"]}
    }

def is_domain(target):
    # Simple regex to check if the target is a domain
    domain_regex = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,6}$"
    return re.match(domain_regex,target) is not None

def get_last_scan_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT scan_id FROM scans ORDER BY scan_id DESC LIMIT 1")
    last_scan = cursor.fetchone()
    conn.close()
    return last_scan[0] if last_scan else None

def get_scan_status(scan_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM scans WHERE scan_id = ?", (scan_id,)) 
    scan = cursor.fetchone()
    conn.close()
    if scan:
        return scan[0] == "complete"
    return False

def get_nmap_status(scan_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM scans WHERE scan_id = ? and tool='nmap'", (scan_id,))
    scan = cursor.fetchone()
    conn.close()
    return scan[0] if scan else None
def get_open_ports(scan_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT results FROM scans WHERE scan_id = ? and tool='nmap'", (scan_id,))
    scan = cursor.fetchone()
    ports=ast.literal_eval(scan[0])
    open_ports = [int(i['port']) for i in ports['ports']]
    return open_ports
 
   
