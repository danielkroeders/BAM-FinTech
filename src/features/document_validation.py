import json
import os
import re
import zipfile
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st

from src.utils.document_storage import (
    DOCUMENT_CATEGORIES,
    list_documents,
    read_document,
)

DOCUMENT_VALIDATION_PROVIDERS = ["Deterministic", "OpenAI API", "Local server"]
MAX_PREVIEW_CHARS = 4500

CATEGORY_EXPECTATIONS = {
    "financial_statements": {
        "label": DOCUMENT_CATEGORIES["financial_statements"],
        "keywords": [
            "financial",
            "statement",
            "revenue",
            "gross profit",
            "operating expenses",
            "free cash flow",
            "cash",
            "debt",
            "equity",
            "balance sheet",
            "income statement",
        ],
        "follow_up": "Ask for recent financial statements or management accounts that reconcile revenue, cash, debt, and equity.",
    },
    "bank_statements": {
        "label": DOCUMENT_CATEGORIES["bank_statements"],
        "keywords": [
            "bank",
            "account",
            "statement",
            "inflow",
            "outflow",
            "ending balance",
            "overdraft",
            "transaction",
            "counterparty",
            "iban",
        ],
        "follow_up": "Ask for recent bank-account statements or a consented PSD2 feed covering balances and transaction history.",
    },
    "tax_returns": {
        "label": DOCUMENT_CATEGORIES["tax_returns"],
        "keywords": [
            "tax",
            "taxable",
            "return",
            "turnover",
            "vat",
            "sales tax",
            "corporate income",
            "assessment",
            "filed",
        ],
        "follow_up": "Ask for the latest filed tax return, VAT status, or final tax assessment.",
    },
    "ownership_kyb": {
        "label": DOCUMENT_CATEGORIES["ownership_kyb"],
        "keywords": [
            "ownership",
            "kyb",
            "ubo",
            "beneficial owner",
            "shareholder",
            "director",
            "registry",
            "registration",
            "sanctions",
            "pep",
        ],
        "follow_up": "Ask for a registry extract, shareholder or UBO register, director evidence, and KYB screening support.",
    },
    "forecast_support": {
        "label": DOCUMENT_CATEGORIES["forecast_support"],
        "keywords": [
            "forecast",
            "pipeline",
            "contracted revenue",
            "projected",
            "assumption",
            "planned debt service",
            "operating costs",
            "runway",
            "growth",
        ],
        "follow_up": "Ask for forecast assumptions, signed-contract support, pipeline evidence, and monthly debt-service planning.",
    },
}


def _api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def _local_api_key():
    return os.getenv("LOCAL_LLM_API_KEY", "local")


def _normalize_local_base_url(base_url):
    normalized = (base_url or "http://localhost:1234/v1").strip().rstrip("/")
    if normalized.endswith("/v1/chat/completions"):
        return normalized[: -len("/chat/completions")]
    if normalized.endswith("/chat/completions"):
        normalized = normalized[: -len("/chat/completions")]
    if not normalized.endswith("/v1"):
        normalized = f"{normalized}/v1"
    return normalized


def _strip_xml(raw_text):
    raw_text = re.sub(r"<[^>]+>", " ", raw_text)
    raw_text = re.sub(r"\s+", " ", raw_text)
    return raw_text.strip()


def _decode_text(content):
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return ""


def _archive_text_preview(content, suffix):
    try:
        archive = zipfile.ZipFile(BytesIO(content))
    except zipfile.BadZipFile:
        return ""

    members = []
    if suffix == ".docx":
        members = ["word/document.xml"]
    elif suffix == ".xlsx":
        members = [
            "xl/sharedStrings.xml",
            "xl/worksheets/sheet1.xml",
            "xl/worksheets/sheet2.xml",
            "xl/worksheets/sheet3.xml",
        ]

    snippets = []
    for member in members:
        try:
            snippets.append(
                _strip_xml(archive.read(member).decode("utf-8", errors="ignore"))
            )
        except KeyError:
            continue
    return "\n".join(snippet for snippet in snippets if snippet)


def text_preview(content, metadata, max_chars=MAX_PREVIEW_CHARS):
    name = str(metadata.get("original_name", ""))
    suffix = f".{name.rsplit('.', 1)[-1].lower()}" if "." in name else ""
    content_type = str(metadata.get("content_type", "")).lower()

    if suffix in {".docx", ".xlsx"}:
        extracted = _archive_text_preview(content, suffix)
        if extracted:
            return extracted[:max_chars], "extracted office text"

    if content_type.startswith("text/") or suffix in {
        ".csv",
        ".txt",
        ".md",
        ".json",
        ".xml",
    }:
        decoded = _decode_text(content)
        if decoded:
            return decoded[:max_chars], "decoded text"

    if suffix == ".pdf" or content[:4] == b"%PDF":
        return (
            "PDF binary detected. Text extraction is not enabled in this MVP check.",
            "binary pdf",
        )
    if suffix in {".png", ".jpg", ".jpeg"} or content_type.startswith("image/"):
        return (
            "Image binary detected. OCR is not enabled in this MVP check.",
            "binary image",
        )
    return (
        "Binary or unsupported file type. Classification uses filename, MIME type, size, and extension only.",
        "metadata only",
    )


def _category_scores(text, filename):
    combined = f"{filename}\n{text}".lower()
    scores = {}
    hits = {}
    for category, spec in CATEGORY_EXPECTATIONS.items():
        matched = [keyword for keyword in spec["keywords"] if keyword in combined]
        scores[category] = len(matched)
        hits[category] = matched[:6]
    return scores, hits


def _status_from_scores(
    expected_category,
    detected_category,
    expected_score,
    top_score,
    preview_source,
    suffix,
):
    if (
        preview_source in {"binary pdf", "binary image", "metadata only"}
        and expected_score < 3
    ):
        return "Needs review", 0.38
    if detected_category == expected_category and expected_score >= 4:
        return "Verified", min(0.95, 0.58 + expected_score * 0.055)
    if (
        detected_category == expected_category
        and expected_score >= 2
        and suffix in {".csv", ".txt", ".md", ".json", ".docx", ".xlsx"}
    ):
        return "Needs review", min(0.74, 0.42 + expected_score * 0.08)
    if (
        detected_category != expected_category
        and top_score >= 3
        and expected_score <= 1
    ):
        return "Mismatch", min(0.9, 0.52 + top_score * 0.07)
    return "Needs review", min(0.65, 0.35 + max(expected_score, top_score) * 0.05)


def deterministic_document_validation(content, metadata, expected_category=None):
    expected_category = expected_category or metadata.get("category")
    expected_label = DOCUMENT_CATEGORIES.get(
        expected_category, str(expected_category or "Unknown")
    )
    preview, preview_source = text_preview(content, metadata)
    filename = str(metadata.get("original_name", ""))
    suffix = f".{filename.rsplit('.', 1)[-1].lower()}" if "." in filename else ""
    scores, hits = _category_scores(preview, filename)
    detected_category = max(scores, key=scores.get) if scores else expected_category
    detected_label = DOCUMENT_CATEGORIES.get(
        detected_category, str(detected_category or "Unknown")
    )
    expected_score = scores.get(expected_category, 0)
    top_score = scores.get(detected_category, 0)
    status, confidence = _status_from_scores(
        expected_category,
        detected_category,
        expected_score,
        top_score,
        preview_source,
        suffix,
    )

    if expected_category not in DOCUMENT_CATEGORIES:
        status = "Needs review"
        confidence = min(confidence, 0.4)

    evidence = hits.get(expected_category, [])
    if status == "Verified":
        rationale = f"The file content and filename contain markers expected for {expected_label.lower()}."
    elif status == "Mismatch":
        rationale = f"The file looks more like {detected_label.lower()} than {expected_label.lower()} based on visible markers."
    else:
        rationale = f"The file needs human confirmation because the visible content is limited or does not strongly prove it is {expected_label.lower()}."

    return {
        "document_id": metadata.get("document_id"),
        "file": metadata.get("original_name"),
        "expected_category": expected_category,
        "expected_label": expected_label,
        "detected_category": detected_category,
        "detected_label": detected_label,
        "status": status,
        "confidence": round(float(confidence), 2),
        "provider": "Deterministic",
        "preview_source": preview_source,
        "rationale": rationale,
        "evidence": evidence,
        "follow_up": CATEGORY_EXPECTATIONS.get(expected_category, {}).get(
            "follow_up",
            "Ask the applicant for clearer source evidence.",
        ),
        "validated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _validation_messages(content, metadata, deterministic_result):
    preview, preview_source = text_preview(content, metadata)
    categories = ", ".join(
        f"{key}: {value}" for key, value in DOCUMENT_CATEGORIES.items()
    )
    user_payload = {
        "document_metadata": {
            "file": metadata.get("original_name"),
            "declared_category": metadata.get("category"),
            "declared_label": metadata.get("category_label"),
            "content_type": metadata.get("content_type"),
            "size_bytes": metadata.get("size_bytes"),
            "sha256_prefix": str(metadata.get("sha256", ""))[:16],
        },
        "preview_source": preview_source,
        "visible_text_preview": preview,
        "deterministic_result": deterministic_result,
        "allowed_categories": DOCUMENT_CATEGORIES,
    }
    return [
        {
            "role": "system",
            "content": (
                "You classify SME loan application evidence. Decide whether the visible document metadata and bounded "
                "text preview match the declared document category. You cannot prove authenticity; report only whether "
                "the file appears to be the expected category. Return strict JSON with keys: status, confidence, "
                "detected_category, rationale, evidence, follow_up. status must be one of Verified, Needs review, Mismatch. "
                f"Allowed categories are: {categories}."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(user_payload, indent=2),
        },
    ]


def _extract_json(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def _coerce_ai_result(payload, fallback, provider):
    if not isinstance(payload, dict):
        result = dict(fallback)
        result["ai_error"] = "AI response was not valid JSON."
        return result

    status = str(payload.get("status", fallback["status"])).strip()
    if status not in {"Verified", "Needs review", "Mismatch"}:
        status = "Needs review"

    detected_category = str(
        payload.get("detected_category", fallback["detected_category"])
    ).strip()
    if detected_category not in DOCUMENT_CATEGORIES:
        detected_category = fallback["detected_category"]

    try:
        confidence = float(payload.get("confidence", fallback["confidence"]))
    except (TypeError, ValueError):
        confidence = fallback["confidence"]
    confidence = max(0.0, min(1.0, confidence))

    evidence = payload.get("evidence", fallback.get("evidence", []))
    if isinstance(evidence, str):
        evidence = [evidence]
    if not isinstance(evidence, list):
        evidence = fallback.get("evidence", [])

    result = dict(fallback)
    result.update(
        {
            "status": status,
            "confidence": round(confidence, 2),
            "detected_category": detected_category,
            "detected_label": DOCUMENT_CATEGORIES.get(
                detected_category, detected_category
            ),
            "provider": provider,
            "rationale": str(payload.get("rationale", fallback["rationale"])).strip()
            or fallback["rationale"],
            "evidence": [str(item)[:160] for item in evidence[:6]],
            "follow_up": str(payload.get("follow_up", fallback["follow_up"])).strip()
            or fallback["follow_up"],
        }
    )
    return result


def _openai_validation(content, metadata, deterministic_result, model):
    key = _api_key()
    if not key:
        result = dict(deterministic_result)
        result["ai_error"] = "OpenAI API key is not configured."
        return result
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key, timeout=30)
        response = client.responses.create(
            model=model or "gpt-4.1-mini",
            input=_validation_messages(content, metadata, deterministic_result),
        )
        return _coerce_ai_result(
            _extract_json(response.output_text), deterministic_result, "OpenAI API"
        )
    except Exception as error:
        result = dict(deterministic_result)
        result["ai_error"] = f"OpenAI document validation failed: {error}"
        return result


def _local_validation(
    content, metadata, deterministic_result, model, base_url=None, api_key=None
):
    if not st.session_state.get("local_llm_settings_saved", False):
        result = dict(deterministic_result)
        result["ai_error"] = "Local server settings have not been saved yet."
        return result
    if not (base_url or "").strip() or not (model or "").strip():
        result = dict(deterministic_result)
        result["ai_error"] = (
            "Local server URL and model name are required before calling the local model."
        )
        return result
    try:
        from openai import OpenAI

        normalized_base_url = _normalize_local_base_url(base_url)
        client = OpenAI(
            api_key=api_key or _local_api_key(),
            base_url=normalized_base_url,
            timeout=45,
        )
        response = client.chat.completions.create(
            model=model,
            messages=_validation_messages(content, metadata, deterministic_result),
            temperature=0.1,
        )
        st.session_state.last_local_llm_base_url = normalized_base_url
        response_text = response.choices[0].message.content
        return _coerce_ai_result(
            _extract_json(response_text), deterministic_result, "Local server"
        )
    except Exception as error:
        result = dict(deterministic_result)
        result["ai_error"] = f"Local document validation failed: {error}"
        return result


def validate_document(
    content,
    metadata,
    provider="Deterministic",
    model=None,
    local_base_url=None,
    local_api_key=None,
):
    deterministic_result = deterministic_document_validation(
        content, metadata, metadata.get("category")
    )
    if provider == "OpenAI API":
        return _openai_validation(content, metadata, deterministic_result, model)
    if provider == "Local server":
        return _local_validation(
            content,
            metadata,
            deterministic_result,
            model,
            local_base_url,
            local_api_key,
        )
    return deterministic_result


def validation_summary(results):
    total = len(results)
    verified = sum(1 for result in results if result.get("status") == "Verified")
    mismatches = sum(1 for result in results if result.get("status") == "Mismatch")
    needs_review = sum(
        1 for result in results if result.get("status") == "Needs review"
    )
    if not total:
        status = "No documents"
    elif mismatches:
        status = "Mismatch found"
    elif needs_review:
        status = "Needs review"
    else:
        status = "Verified"
    return {
        "total": total,
        "verified": verified,
        "needs_review": needs_review,
        "mismatches": mismatches,
        "status": status,
    }


def run_document_validation(
    session_id,
    application_id,
    provider="Deterministic",
    model=None,
    local_base_url=None,
    local_api_key=None,
    root=None,
):
    results = []
    for document in list_documents(session_id, application_id, root=root):
        content, metadata = read_document(
            session_id, application_id, document["document_id"], root=root
        )
        results.append(
            validate_document(
                content,
                metadata,
                provider=provider,
                model=model,
                local_base_url=local_base_url,
                local_api_key=local_api_key,
            )
        )

    summary = validation_summary(results)
    return {
        "run_id": f"DOCVAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "application_id": str(application_id),
        "provider_requested": provider,
        "provider_used": provider if provider == "Deterministic" else provider,
        "model": model or "",
        "validated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary,
        "results": results,
    }


def validation_results_table(results):
    return pd.DataFrame(
        [
            {
                "Category": result.get("expected_label"),
                "File": result.get("file"),
                "Status": result.get("status"),
                "Confidence": f"{float(result.get('confidence', 0)):.0%}",
                "Detected as": result.get("detected_label"),
                "Provider": result.get("provider"),
                "Reason": result.get("rationale"),
            }
            for result in results
        ]
    )
