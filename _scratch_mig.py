"""Scratch harness: exercise the Migration Simulator with a 40-finding synthetic scan."""
import streamlit as st

from dashboard.components.views.migration_simulator import render_migration_and_simulator

findings = []
for i in range(10):
    findings.append({"algorithm": "RSA-2048", "file_path": f"src/a{i}.py", "line_number": i,
                     "category": "Asymmetric", "quantum_risk": "CRITICAL", "severity": "CRITICAL",
                     "confidence": 0.9, "recommendation": {"replacement": "ML-KEM"}})
for i in range(10):
    findings.append({"algorithm": "SHA-1", "file_path": f"src/b{i}.py", "line_number": i,
                     "category": "Hash", "quantum_risk": "VULNERABLE", "severity": "HIGH",
                     "confidence": 0.8, "recommendation": {"replacement": "SHA3-256"}})
for i in range(20):
    findings.append({"algorithm": "AES-128", "file_path": f"src/c{i}.py", "line_number": i,
                     "category": "Symmetric", "quantum_risk": "PARTIAL", "severity": "MEDIUM",
                     "confidence": 0.7, "recommendation": {"replacement": "AES-256"}})

render_migration_and_simulator({"findings": findings, "summary": {}, "total_files_scanned": 40})
