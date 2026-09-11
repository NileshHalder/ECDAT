"""Multi-source cryptographic discovery and evidence enrichment.

The scanner treats source code, binaries, manifests, configuration, certificate
files, container definitions, and API/TLS declarations as evidence sources.
One unreadable file never stops a scan.
"""
from __future__ import annotations

import json
import os
import re
import ssl
from pathlib import Path

from .patterns import PATTERNS

MAX_FILE_BYTES = 20 * 1024 * 1024
BINARY_EXTENSIONS = {".dll", ".exe", ".so", ".dylib", ".jar", ".class", ".bin", ".elf"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".conf", ".properties", ".env", ".xml"}
DEPENDENCY_FILES = {"requirements.txt", "package.json", "pom.xml", "pyproject.toml", "go.mod", "cargo.toml"}
CRYPTO_DEPENDENCIES = {"cryptography", "pycryptodome", "pycryptodomex", "bcrypt", "argon2", "openssl", "bouncycastle", "crypto-js", "jose"}


def score_confidence(line: str, file_path: str) -> float:
    stripped = line.strip()
    if stripped.startswith(("#", "//", "/*", "*")):
        return 0.3
    if "test" in file_path.lower() or "_test." in file_path:
        return 0.5
    return 1.0


def _read_text(file_path: str) -> tuple[list[str], str, bool]:
    """Read text or printable strings from a binary; skip oversized files."""
    try:
        if os.path.getsize(file_path) > MAX_FILE_BYTES:
            return [], "", False
        raw = Path(file_path).read_bytes()
    except OSError:
        return [], "", False
    binary = Path(file_path).suffix.lower() in BINARY_EXTENSIONS or b"\x00" in raw[:4096]
    if binary:
        # Preserve printable strings only; this finds embedded cipher names and
        # TLS configuration without pretending to decompile the executable.
        text = "\n".join(match.decode("latin-1") for match in re.findall(rb"[ -~]{4,}", raw))
    else:
        text = raw.decode("utf-8", errors="ignore")
    return text.splitlines(keepends=True), text, binary


def _source_type(file_path: str, binary: bool) -> str:
    name, suffix = Path(file_path).name.lower(), Path(file_path).suffix.lower()
    if binary:
        return "binary"
    if name in DEPENDENCY_FILES:
        return "dependency manifest"
    if name == "dockerfile" or suffix in {".dockerfile", ".containerfile"}:
        return "container definition"
    if suffix in {".pem", ".crt", ".cer", ".der"}:
        return "certificate"
    if suffix in CONFIG_EXTENSIONS:
        return "configuration"
    return "source code"


def _key_metadata(algorithm: str, context: str) -> tuple[str, int | None, str | None]:
    category = algorithm.upper()
    if category in {"RSA", "ECDSA", "DIFFIE-HELLMAN", "ML-KEM", "ML-DSA", "SLH-DSA"}:
        key_type = "asymmetric"
    elif category in {"AES", "DES", "3DES", "CHACHA20"}:
        key_type = "symmetric"
    elif category in {"MD5", "SHA-1", "SHA-256", "SHA-3"}:
        key_type = "hash"
    elif category in {"HMAC"}:
        key_type = "MAC"
    elif category in {"PBKDF2", "BCRYPT", "ARGON2"}:
        key_type = "KDF"
    else:
        key_type = "unknown"
    match = re.search(r"\b(128|192|224|256|384|512|1024|1536|2048|3072|4096|7680|8192)\b", context)
    key_size = int(match.group(1)) if match else None
    protocol_match = re.search(r"\b(?:TLSv?1\.[0-3]|SSLv?[0-3]|HTTPS|SSH|IPsec)\b", context, re.I)
    return key_type, key_size, protocol_match.group(0).upper() if protocol_match else None


def _usage(context: str) -> str:
    text = context.lower()
    if any(word in text for word in ("sign", "signature", "verify")):
        return "digital signature"
    if any(word in text for word in ("encrypt", "decrypt", "cipher")):
        return "encryption"
    if any(word in text for word in ("hash", "digest", "checksum")):
        return "hashing"
    if any(word in text for word in ("token", "auth", "login", "password")):
        return "authentication"
    if "key" in text:
        return "key management"
    return "cryptographic usage"


def _certificate_info(file_path: str) -> dict:
    """Extract standard-library certificate fields for PEM certificates when available."""
    if Path(file_path).suffix.lower() not in {".pem", ".crt", ".cer"}:
        return {}
    try:
        cert = ssl._ssl._test_decode_cert(file_path)
        return {
            "subject": "/".join("=".join(part) for group in cert.get("subject", ()) for part in group),
            "issuer": "/".join("=".join(part) for group in cert.get("issuer", ()) for part in group),
            "serial_number": cert.get("serialNumber"),
            "not_before": cert.get("notBefore"),
            "not_after": cert.get("notAfter"),
        }
    except (OSError, ssl.SSLError, ValueError):
        return {}


def _finding(*, pattern_id: str, algorithm: str, category: str, file_path: str, line_number: int,
             context: list[str], quantum_risk: str, severity: str, source_type: str,
             certificate_info: dict | None = None) -> dict:
    context_text = "".join(context)
    key_type, key_size, protocol = _key_metadata(algorithm, context_text)
    return {
        "pattern_id": pattern_id,
        "algorithm": algorithm,
        "category": category,
        "file_path": file_path,
        "line_number": line_number,
        "context": context,
        "quantum_risk": quantum_risk,
        "severity": severity,
        "confidence": score_confidence(context[0] if context else "", file_path),
        "source_type": source_type,
        "key_type": key_type,
        "key_size": key_size,
        "protocol": protocol,
        "usage": _usage(context_text),
        "application": Path(file_path).parent.name or "repository root",
        "certificate_info": certificate_info or {},
    }


def _auxiliary_findings(file_path: str, lines: list[str], full_text: str, source_type: str) -> list[dict]:
    """Discover dependency, container, endpoint and modern-TLS evidence."""
    findings: list[dict] = []
    lower_name = Path(file_path).name.lower()
    for line_no, line in enumerate(lines, start=1):
        context = lines[max(0, line_no - 2):line_no + 1]
        if lower_name in DEPENDENCY_FILES:
            for dependency in CRYPTO_DEPENDENCIES:
                if re.search(rf"(?<![\w-]){re.escape(dependency)}(?![\w-])", line, re.I):
                    findings.append(_finding(pattern_id="DEP-001", algorithm=f"Crypto dependency: {dependency}", category="dependency",
                                             file_path=file_path, line_number=line_no, context=context, quantum_risk="UNKNOWN",
                                             severity="info", source_type="dependency manifest"))
        if source_type == "container definition" and re.search(r"^\s*(FROM|RUN|COPY|EXPOSE)\b", line, re.I):
            findings.append(_finding(pattern_id="CONT-001", algorithm="Container workload", category="container",
                                     file_path=file_path, line_number=line_no, context=context, quantum_risk="UNKNOWN",
                                     severity="info", source_type=source_type))
        if re.search(r"(?:@(?:app|router)\.(?:get|post|put|delete|patch)|@(Get|Post|Put|Delete|Patch)Mapping|\b(?:app|router)\.(?:get|post|put|delete|patch)\s*\()", line):
            findings.append(_finding(pattern_id="API-001", algorithm="API endpoint", category="api",
                                     file_path=file_path, line_number=line_no, context=context, quantum_risk="UNKNOWN",
                                     severity="info", source_type="API endpoint"))
        if re.search(r"TLSv?1\.3", line, re.I):
            findings.append(_finding(pattern_id="TLS-002", algorithm="TLS 1.3", category="protocol",
                                     file_path=file_path, line_number=line_no, context=context, quantum_risk="SAFE",
                                     severity="info", source_type=source_type))
    return findings


def scan_file(file_path: str, patterns=None) -> list[dict]:
    patterns = patterns or PATTERNS
    lines, full_text, binary = _read_text(file_path)
    if not full_text:
        return []
    source_type = _source_type(file_path, binary)
    certificate_info = _certificate_info(file_path)
    findings: list[dict] = []
    for pattern in patterns:
        for match in re.finditer(pattern["regex"], full_text):
            line_no = full_text[:match.start()].count("\n") + 1
            context = lines[max(0, line_no - 4):min(len(lines), line_no + 3)]
            findings.append(_finding(pattern_id=pattern["id"], algorithm=pattern["algorithm"], category=pattern["category"],
                                     file_path=file_path, line_number=line_no, context=context, quantum_risk=pattern["quantum_risk"],
                                     severity=pattern["severity"], source_type=source_type, certificate_info=certificate_info))
    findings.extend(_auxiliary_findings(file_path, lines, full_text, source_type))
    return findings


def scan_directory(root_path: str, patterns=None) -> list[dict]:
    from .walker import walk_files

    all_findings: list[dict] = []
    for file_path in walk_files(root_path):
        all_findings.extend(scan_file(file_path, patterns))
    return all_findings
