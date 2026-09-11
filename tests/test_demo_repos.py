import time

import requests

API = 'http://127.0.0.1:8000'
repos = [
    ("1_legacy_fintech_core", r"d:\ecdat_starter\ecdat\demo_repos\1_legacy_fintech_core"),
    ("2_hybrid_cloud_microservice", r"d:\ecdat_starter\ecdat\demo_repos\2_hybrid_cloud_microservice"),
    ("3_quantum_ready_defense_app", r"d:\ecdat_starter\ecdat\demo_repos\3_quantum_ready_defense_app"),
]

def main():
    print("Scanning demo repositories...\n")
    for name, path in repos:
        s = requests.post(f"{API}/scan", params={"path": path}).json()
        sid = s["scan_id"]
        for _ in range(10):
            time.sleep(0.3)
            r = requests.get(f"{API}/results/{sid}").json()
            if r.get("status") == "completed":
                break
                
        score = r.get("migration_readiness_score", 0)
        summary = r.get("summary", {})
        findings = r.get("findings", [])
        
        if score >= 70:
            verdict = "Low quantum risk (Quantum-Safe)"
        elif score >= 40:
            verdict = "Moderate risk — migrate soon"
        else:
            verdict = "High risk — act now"
            
        print("==================================================")
        print(f"Repository: {name}")
        print(f"Score:      {score}% -> {verdict}")
        print(f"Breakdown:  {summary}")
        print(f"Findings:   {len(findings)} detected")
        print("--------------------------------------------------")
        for f in findings:
            algo = f['algorithm']
            risk = f['quantum_risk']
            sev = f['severity']
            fname = f['file_path'].split('\\')[-1]
            line = f['line_number']
            rec = f.get('recommendation')
            rec_str = f"-> Replace: {rec['replacement']} ({rec.get('fips') or 'FIPS'})" if rec else "-> Quantum-Safe"
            print(f"  • [{risk:<10}] {algo:<15} ({sev:<8}) @ {fname}:{line:<3} {rec_str}")
        print()


if __name__ == "__main__":
    main()
