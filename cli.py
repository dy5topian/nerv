import requests
import sys
import os
import time
from typing import Dict, Any

API_URL = "http://localhost:8000"

class ScanCLI:
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
        



    def submit_scan(self, target: str) -> Dict[str, Any]:
        """Submit a new scan for the specified target"""
        try:
            response = requests.post(
                f"{self.api_url}/scan",
                json={"target": target}
            )
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error submitting scan: {e}")
            sys.exit(1)

    def get_results(self, scan_id: str) -> Dict[str, Any]:
        """Get results for a specific scan ID"""
        try:
            response = requests.get(f"{self.api_url}/results/{scan_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching results: {e}")
            sys.exit(1)

    def wait_for_completion(self, scan_id: str, poll_interval: int = 5) -> Dict[str, Any]:
        """Wait for scan completion and return results"""
        print(f"Waiting for scan {scan_id} to complete...")
        while True:
            results = self.get_results(scan_id)
            if results["status"] == "completed":
                return results
            print("Scan in progress...")
            time.sleep(poll_interval)

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <target>")
        sys.exit(1)
    
    target = sys.argv[1]
    cli = ScanCLI()
    
    # Submit scan
    print(f"Submitting scan for target: {target}")
    scan = cli.submit_scan(target)
    scan_id = scan["scan_id"]
    print(f"Scan submitted! ID: {scan_id}")
    
    # Wait for completion and get results
    results = cli.wait_for_completion(scan_id)
    print("\nScan Results:")
    print(f"Status: {results['status']}")
    for result in results["results"]:
        print(f"\nTool: {result['tool']}")
        print(f"Status: {result['status']}")
        if result["results"]:
            print(f"Results: {result['results']}")

if __name__ == "__main__":
    main()
