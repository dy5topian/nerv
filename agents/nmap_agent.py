from celery import shared_task
import subprocess
import xml.etree.ElementTree as ET

@shared_task
def run_nmap(target, options="-sV"):
    """
    Run an nmap scan on the specified target with the given options.
    
    :param target: The target to scan.
    :param options: The nmap options to use.
    :return: The output of the nmap scan.
    """
    # Improved input sanitization
    target = target.replace(";", "").replace("&", "").replace("|", "").replace("$", "")
    cmd = f"nmap {options} {target} -oX -"
    
    try:
        # Execute the nmap command
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=300,
            check=True  # Ensure subprocess raises an error on failure
        )
        root = ET.fromstring(result.stdout)
        ports = []
        for port in root.findall(".//port"):
            ports.append({
                "port": port.attrib['portid'],
                "service": port.find('service').attrib.get('name', 'unknown')
            })
        return {"status": "success", "ports": ports}
    except subprocess.CalledProcessError as e:
        # Handle errors in the nmap execution
        return {"status": "error", "message": f"An error occurred: {e.stderr}"}
    except ET.ParseError as e:
        return {"status": "error", "message": f"XML parsing error: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

