import subprocess
import json

def run_whatweb(target):
    target = target.replace(";", "").replace("&", "")
    cmd = f"whatweb {target} --log-json=-"
    
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=60
        )
        return {"status": "success", "data": json.loads(result.stdout)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
