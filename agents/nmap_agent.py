import subprocess
import xml.etree.ElementTree as ET

def run_nmap(target, options="-sV"):
    # Improved input sanitization
    target = target.replace(";", "").replace("&", "").replace("|", "").replace("$", "")
    cmd = f"nmap {options} {target} -oX -"
    
    try:
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
        return {"status": "error", "message": f"Command failed: {e}"}
    except ET.ParseError as e:
        return {"status": "error", "message": f"XML parsing error: {e}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
