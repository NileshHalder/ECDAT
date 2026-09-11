import json
import time

import requests

API = 'http://127.0.0.1:8000'
path = r'd:\ecdat_starter\ecdat\samples'

def main():
    print("--- 1. Health Check ---")
    h = requests.get(f"{API}/health")
    print("Health status:", h.status_code, h.json())

    print("\n--- 2. Submitting Scan ---")
    s = requests.post(f"{API}/scan", params={"path": path}).json()
    sid = s["scan_id"]
    print("Scan ID:", sid)

    print("\n--- 3. Polling Results ---")
    for i in range(15):
        time.sleep(0.3)
        r = requests.get(f"{API}/results/{sid}").json()
        if r.get("status") == "completed":
            print(f"Completed after {i * 0.3:.1f}s")
            break

    print("Status:", r.get("status"))
    print("Migration Readiness Score:", r.get("migration_readiness_score"))
    print("Summary breakdown:", r.get("summary"))
    print("Total files with findings:", r.get("total_files_scanned"))
    findings = r.get("findings", [])
    print("Total findings:", len(findings))

    print("\n--- 4. Findings Detail ---")
    for idx, f in enumerate(findings, 1):
        rec = f.get("recommendation", {})
        rep = f"{rec.get('replacement')} ({rec.get('fips')})" if rec else "None"
        print(f"{idx}. [{f['quantum_risk']}] {f['algorithm']} -> {f['file_path']}:{f['line_number']}")
        print(f"   Severity: {f['severity']} | Confidence: {f['confidence']} | Replace with: {rep}")

    print("\n--- 5. CBOM Verification ---")
    cbom = requests.get(f"{API}/cbom/{sid}").json()
    print("bomFormat:", cbom.get("bomFormat"))
    print("specVersion:", cbom.get("specVersion"))
    print("serialNumber:", cbom.get("serialNumber"))
    print("Total components:", len(cbom.get("components", [])))
    if cbom.get("components"):
        print("Sample CBOM component:", json.dumps(cbom["components"][0], indent=2))


if __name__ == "__main__":
    main()
