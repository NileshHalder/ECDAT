"""
API routes: /scan, /results/{scan_id}, /cbom/{scan_id}, /health.
Thin layer — delegates to scanner/, cbom/ modules. No logic lives here.
"""
import os
import shutil
import tempfile
import uuid
import zipfile
import subprocess
import stat
from datetime import datetime, timezone
from pathlib import PurePosixPath
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, File, UploadFile

from cbom.export import build_cbom
from scanner.analyzer import scan_directory
from scanner.evidence import fuse_evidence
from scanner.walker import walk_files
from scanner.recommend import attach_recommendations
from scanner.risk import assess_findings, readiness_score, summarize

from . import db

router = APIRouter()


def safe_extract_zip(archive: zipfile.ZipFile, destination: str):
    """Extract a ZIP only after rejecting traversal paths, links, and ZIP bombs."""
    members = archive.infolist()
    if len(members) > 5_000:
        raise ValueError("Archive contains too many files.")
    if sum(member.file_size for member in members) > 250 * 1024 * 1024:
        raise ValueError("Archive exceeds the 250 MB extracted-size limit.")

    for member in members:
        normalized_name = member.filename.replace("\\", "/")
        path = PurePosixPath(normalized_name)
        is_symlink = stat.S_IFMT(member.external_attr >> 16) == stat.S_IFLNK
        if path.is_absolute() or ".." in path.parts or is_symlink:
            raise ValueError("Archive contains an unsafe file path.")

    for member in members:
        archive.extract(member, destination)


def run_scan_job(scan_id: str, target_path: str):
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        if not os.path.isdir(target_path):
            raise ValueError("The selected scan location is not available.")
        total_files_scanned = sum(1 for _ in walk_files(target_path))
        findings = fuse_evidence(assess_findings(attach_recommendations(scan_directory(target_path))))
        db.save_scan({
            "scan_id": scan_id,
            "target_path": target_path,
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
            "total_files_scanned": total_files_scanned,
            "files_with_findings": len({f["file_path"] for f in findings}),
            "migration_readiness_score": readiness_score(findings),
            "findings": findings,
            "summary": summarize(findings),
        })
    except Exception as exc:
        db.save_scan({
            "scan_id": scan_id,
            "target_path": target_path,
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
            "findings": [],
            "summary": {"error": str(exc)},
        })


def run_github_scan_job(scan_id: str, repo_url: str):
    """Clone a public GitHub repository into an isolated temporary directory."""
    clone_dir = tempfile.mkdtemp(prefix=f"ecdat_github_{scan_id[:8]}_")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--", repo_url, clone_dir],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        run_scan_job(scan_id, clone_dir)
    except (OSError, subprocess.SubprocessError):
        db.save_scan({
            "scan_id": scan_id,
            "target_path": repo_url,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
            "findings": [],
            "summary": {"error": "Unable to clone the GitHub repository."},
        })
    finally:
        shutil.rmtree(clone_dir, ignore_errors=True)


@router.post("/scan")
def start_scan(path: str, background_tasks: BackgroundTasks):
    scan_id = str(uuid.uuid4())
    db.save_scan({"scan_id": scan_id, "target_path": path, "status": "running"})
    background_tasks.add_task(run_scan_job, scan_id, path)
    return {"scan_id": scan_id}


@router.post("/scan/github")
def start_github_scan(repo_url: str, background_tasks: BackgroundTasks):
    """Start a scan for a public HTTPS GitHub repository."""
    parsed = urlparse(repo_url)
    if parsed.scheme != "https" or parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return {"error": "Provide a public HTTPS GitHub repository URL."}
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2:
        return {"error": "Use the format https://github.com/owner/repository."}

    scan_id = str(uuid.uuid4())
    normalized_url = f"https://github.com/{path_parts[0]}/{path_parts[1].removesuffix('.git')}.git"
    db.save_scan({"scan_id": scan_id, "target_path": normalized_url, "status": "running"})
    background_tasks.add_task(run_github_scan_job, scan_id, normalized_url)
    return {"scan_id": scan_id}


@router.post("/scan/upload")
async def start_upload_scan(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
):
    scan_id = str(uuid.uuid4())
    temp_dir = tempfile.mkdtemp(prefix=f"ecdat_scan_{scan_id[:8]}_")

    for upload_file in files:
        filename = os.path.basename(upload_file.filename or "uploaded_file")
        file_dest = os.path.join(temp_dir, filename)

        # Handle zip archive uploads (folder upload)
        if filename.lower().endswith(".zip"):
            zip_temp = os.path.join(temp_dir, "_archive.zip")
            with open(zip_temp, "wb") as f_out:
                shutil.copyfileobj(upload_file.file, f_out)
            try:
                with zipfile.ZipFile(zip_temp, "r") as z:
                    safe_extract_zip(z, temp_dir)
                os.remove(zip_temp)
            except (ValueError, zipfile.BadZipFile) as exc:
                shutil.rmtree(temp_dir, ignore_errors=True)
                db.save_scan({
                    "scan_id": scan_id,
                    "target_path": filename,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "status": "failed",
                    "findings": [],
                    "summary": {"error": f"The uploaded archive could not be processed: {exc}"},
                })
                return {"scan_id": scan_id}
        else:
            os.makedirs(os.path.dirname(file_dest), exist_ok=True)
            with open(file_dest, "wb") as f_out:
                shutil.copyfileobj(upload_file.file, f_out)

    db.save_scan({"scan_id": scan_id, "target_path": temp_dir, "status": "running"})
    background_tasks.add_task(run_scan_job, scan_id, temp_dir)
    return {"scan_id": scan_id, "target_path": temp_dir}


@router.get("/results/{scan_id}")
def get_results(scan_id: str):
    scan = db.get_scan(scan_id)
    if not scan:
        return {"error": "scan not found"}
    return scan


@router.get("/cbom/{scan_id}")
def get_cbom(scan_id: str):
    scan = db.get_scan(scan_id)
    if not scan:
        return {"error": "scan not found"}
    return build_cbom(scan["findings"])


@router.get("/health")
def health():
    return {"status": "ok"}
