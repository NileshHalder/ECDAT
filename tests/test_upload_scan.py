"""Tests for the archive upload scan workflow.

The handler is called directly so pytest does not require a separate Uvicorn
process during collection.
"""
import asyncio
import io
import zipfile

from fastapi import BackgroundTasks, UploadFile
import pytest

from api import db
from api.routes import start_upload_scan


@pytest.fixture(autouse=True)
def initialise_database():
    db.init_db()


def test_uploaded_zip_is_scanned():
    archive_data = io.BytesIO()
    with zipfile.ZipFile(archive_data, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "legacy_auth.py",
            "from cryptography.hazmat.primitives.asymmetric import rsa\n"
            "key = rsa.generate_private_key(65537, 2048)\n",
        )
        archive.writestr("utils/hasher.py", "import hashlib\nhashlib.md5(b'test')\n")

    upload = UploadFile(filename="test_repo.zip", file=io.BytesIO(archive_data.getvalue()))
    tasks = BackgroundTasks()
    response = asyncio.run(start_upload_scan(background_tasks=tasks, files=[upload]))

    assert "scan_id" in response
    asyncio.run(tasks())
    result = db.get_scan(response["scan_id"])

    assert result is not None
    assert result["status"] == "completed"
    assert {finding["algorithm"] for finding in result["findings"]} >= {"RSA", "MD5"}
