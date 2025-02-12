import subprocess
import xml.etree.ElementTree as ET

def run_nmap(target, options="-sV"):
    # Prevent command injection
    target = target.replace(";", "").replace("&", "")
    cmd = f"nmap {options} {target} -oX -"
    
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=300
        )
        root = ET.fromstring(result.stdout)
        ports = []
        for port in root.findall(".//port"):
            ports.append({
                "port": port.attrib['portid'],
                "service": port.find('service').attrib.get('name', 'unknown')
            })
        return {"status": "success", "ports": ports}
    except Exception as e:
        return {"status": "error", "message": str(e)}
