"""
Unit tests for the scanner engine, run against samples/ and demo_repos/.
Run with: python -m unittest discover tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scanner.analyzer import scan_directory, scan_file
from scanner.recommend import attach_recommendations
from scanner.risk import assess_findings, mosca_score, readiness_score
from scanner.impact import analyze_what_if
from scanner.evidence import fuse_evidence
from cbom.export import build_cbom

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "samples")
DEMO_REPOS_DIR = os.path.join(os.path.dirname(__file__), "..", "demo_repos")


class TestScannerEngine(unittest.TestCase):

    def test_detects_rsa_in_vulnerable_sample(self):
        findings = scan_file(os.path.join(SAMPLES_DIR, "sample_vulnerable.py"))
        algorithms = [f["algorithm"] for f in findings]
        self.assertIn("RSA", algorithms)
        self.assertIn("MD5", algorithms)
        self.assertIn("SHA-1", algorithms)

    def test_rsa_is_classified_vulnerable(self):
        findings = scan_file(os.path.join(SAMPLES_DIR, "sample_vulnerable.py"))
        rsa_findings = [f for f in findings if f["algorithm"] == "RSA"]
        self.assertTrue(len(rsa_findings) > 0)
        self.assertEqual(rsa_findings[0]["quantum_risk"], "VULNERABLE")

    def test_safe_sample_has_no_vulnerable_findings(self):
        findings = scan_file(os.path.join(SAMPLES_DIR, "sample_safe.py"))
        vulnerable = [f for f in findings if f["quantum_risk"] == "VULNERABLE"]
        self.assertEqual(len(vulnerable), 0)

    def test_readiness_score_range(self):
        findings = scan_file(os.path.join(SAMPLES_DIR, "sample_vulnerable.py"))
        score = readiness_score(findings)
        self.assertTrue(0 <= score <= 100)

    def test_mosca_score_labels(self):
        result = mosca_score("asymmetric")
        self.assertIn(result["risk_label"], ("CRITICAL - At risk now", "HIGH - Migrate soon", "LOW - Monitor"))

    def test_recommendations_attached_for_vulnerable(self):
        findings = scan_file(os.path.join(SAMPLES_DIR, "sample_vulnerable.py"))
        findings = attach_recommendations(findings)
        for f in findings:
            if f["quantum_risk"] in ("VULNERABLE", "PARTIAL"):
                self.assertIsNotNone(f["recommendation"])

    def test_assessment_adds_hndl_and_reason(self):
        findings = assess_findings(scan_file(os.path.join(SAMPLES_DIR, "sample_vulnerable.py")))
        rsa = next(f for f in findings if f["algorithm"] == "RSA")
        self.assertIn(rsa["risk_level"], {"HIGH", "CRITICAL"})
        self.assertTrue(rsa["hndl"]["hndl_risk"])
        self.assertTrue(rsa["risk_reason"])

    def test_cbom_contains_scan_derived_relationships(self):
        findings = assess_findings(scan_file(os.path.join(SAMPLES_DIR, "sample_vulnerable.py")))
        cbom = build_cbom(findings)
        self.assertTrue(cbom["graph"]["nodes"])
        relationship_types = {edge["type"] for edge in cbom["graph"]["relationships"]}
        self.assertIn("implements", relationship_types)

    def test_what_if_counts_dependency_blast_radius(self):
        findings = [
            {
                "algorithm": "RSA", "file_path": "payments/api.py", "line_number": 10,
                "application": "payment-service", "purpose": "Digital Signature",
                "business_criticality": "HIGH", "risk_level": "CRITICAL",
                "certificate": "payments.example",
            },
            {
                "algorithm": "RSA", "file_path": "identity/auth.py", "line_number": 20,
                "application": "identity-service", "purpose": "Authentication",
                "business_criticality": "HIGH", "risk_level": "HIGH",
                "certificate": "identity.example",
            },
            {
                "algorithm": "AES", "file_path": "payments/api.py", "line_number": 30,
                "application": "payment-service", "purpose": "Encryption",
            },
        ]
        impact = analyze_what_if(findings, "RSA")
        self.assertEqual(impact["affected_assets"], 2)
        self.assertEqual(impact["affected_applications"], 2)
        self.assertEqual(impact["affected_certificates"], 2)
        self.assertEqual(impact["critical_systems"], 2)
        self.assertEqual(len(impact["paths"]), 2)

    def test_evidence_fusion_detects_cross_channel_conflict(self):
        findings = fuse_evidence([
            {"algorithm": "RSA", "source_type": "source code", "application": "payments"},
            {"algorithm": "ECDSA", "source_type": "certificate", "application": "payments"},
            {"algorithm": "ECDSA", "source_type": "API endpoint", "application": "payments"},
        ])
        fusion = findings[0]["evidence_fusion"]
        self.assertEqual(fusion["status"], "Evidence conflict detected")
        self.assertEqual(fusion["observations"]["network"], ["ECDSA"])
        self.assertTrue(fusion["confidence"] < 0.8)
        self.assertTrue(fusion["reasons"])

    def test_demo_repo_quantum_safe(self):
        pqc_repo = os.path.join(DEMO_REPOS_DIR, "3_quantum_ready_defense_app")
        findings = scan_directory(pqc_repo)
        vulnerable = [f for f in findings if f["quantum_risk"] == "VULNERABLE"]
        self.assertEqual(len(vulnerable), 0)
        score = readiness_score(findings)
        self.assertEqual(score, 100.0)

    def test_scan_uploaded_zip(self):
        import io
        import shutil
        import tempfile
        import zipfile

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("auth.py", "from cryptography.hazmat.primitives.asymmetric import rsa\nk = rsa.generate_private_key(65537, 2048)\n")
        
        temp_dir = tempfile.mkdtemp()
        try:
            zip_buf.seek(0)
            with zipfile.ZipFile(zip_buf, "r") as z:
                z.extractall(temp_dir)
            findings = scan_directory(temp_dir)
            self.assertTrue(any(f["algorithm"] == "RSA" for f in findings))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
