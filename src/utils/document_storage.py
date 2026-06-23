import hashlib
import json
import mimetypes
import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4


DOCUMENT_ROOT = Path(__file__).resolve().parents[2] / ".tmp" / "sme_documents"
DOCUMENT_CATEGORIES = {
    "financial_statements": "Financial statements",
    "bank_statements": "Bank statements",
    "tax_returns": "Tax returns",
    "ownership_kyb": "Ownership / KYB",
    "forecast_support": "Forecast support",
}


def _safe_segment(value, fallback="item"):
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", str(value or "")).strip("-_")
    return cleaned[:80] or fallback


def _application_dir(session_id, application_id, root=None):
    base = Path(root) if root else DOCUMENT_ROOT
    return base / _safe_segment(session_id, "session") / _safe_segment(application_id, "application")


def _manifest_path(session_id, application_id, root=None):
    return _application_dir(session_id, application_id, root=root) / "manifest.json"


def _load_manifest(session_id, application_id, root=None):
    path = _manifest_path(session_id, application_id, root=root)
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return payload if isinstance(payload, list) else []


def _write_manifest(session_id, application_id, documents, root=None):
    path = _manifest_path(session_id, application_id, root=root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(documents, indent=2), encoding="utf-8")
    temp_path.replace(path)


def save_document(session_id, application_id, category, filename, content, content_type=None, root=None):
    if category not in DOCUMENT_CATEGORIES:
        raise ValueError(f"Unsupported document category: {category}")
    if not isinstance(content, bytes) or not content:
        raise ValueError("Document content must contain bytes.")

    original_name = Path(str(filename or "document")).name
    suffix = Path(original_name).suffix.lower()[:12]
    digest = hashlib.sha256(content).hexdigest()
    documents = _load_manifest(session_id, application_id, root=root)

    for document in documents:
        if document.get("category") == category and document.get("sha256") == digest:
            return document, False

    document_id = f"DOC-{uuid4().hex[:12]}"
    stored_name = f"{document_id}{suffix}"
    directory = _application_dir(session_id, application_id, root=root)
    category_dir = directory / category
    category_dir.mkdir(parents=True, exist_ok=True)
    file_path = category_dir / stored_name
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    temp_path.write_bytes(content)
    temp_path.replace(file_path)

    document = {
        "document_id": document_id,
        "application_id": str(application_id),
        "category": category,
        "category_label": DOCUMENT_CATEGORIES[category],
        "original_name": original_name,
        "stored_name": stored_name,
        "content_type": content_type or mimetypes.guess_type(original_name)[0] or "application/octet-stream",
        "size_bytes": len(content),
        "sha256": digest,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    documents.append(document)
    _write_manifest(session_id, application_id, documents, root=root)
    return document, True


def list_documents(session_id, application_id, category=None, root=None):
    documents = _load_manifest(session_id, application_id, root=root)
    if category:
        documents = [document for document in documents if document.get("category") == category]
    return sorted(documents, key=lambda item: item.get("uploaded_at", ""), reverse=True)


def read_document(session_id, application_id, document_id, root=None):
    documents = _load_manifest(session_id, application_id, root=root)
    document = next((item for item in documents if item.get("document_id") == document_id), None)
    if not document:
        raise FileNotFoundError(f"Unknown document: {document_id}")
    path = (
        _application_dir(session_id, application_id, root=root)
        / _safe_segment(document.get("category"))
        / Path(document.get("stored_name", "")).name
    )
    if not path.exists():
        raise FileNotFoundError(document.get("original_name", document_id))
    return path.read_bytes(), document


def document_counts(session_id, application_id, root=None):
    counts = {category: 0 for category in DOCUMENT_CATEGORIES}
    for document in list_documents(session_id, application_id, root=root):
        category = document.get("category")
        if category in counts:
            counts[category] += 1
    return counts


def clear_session_documents(session_id, root=None):
    base = Path(root) if root else DOCUMENT_ROOT
    target = base / _safe_segment(session_id, "session")
    if not target.exists():
        return
    for path in sorted(target.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()
    target.rmdir()
