import requests
import sys

API_URL = "http://localhost:8000"

def submit_scan(target):
    response = requests.post(f"{API_URL}/scan", json={"target": target})
    return response.json()

def get_results(scan_id):
    response = requests.get(f"{API_URL}/results/{scan_id}")
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cli.py <target>")
        sys.exit(1)
    
    target = sys.argv[1]
    scan = submit_scan(target)
    print(f"Scan submitted! ID: {scan['scan_id']}")
    print(f"Check results with: curl {API_URL}/results/{scan['scan_id']}")
