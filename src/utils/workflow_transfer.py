# SME-to-lender snapshot transfer helpers for the submitted intake flow.
# The core rule is snapshot ownership: the SME edits a live draft, submission
# stores a copy, and the lender reviews that copy even if the SME edits later.
SME_SUBMISSION_SOURCE = "SME Portal submission"


def _connection_count(submission):
    # Support both the current integer field and older dict-shaped submission
    # records from previous demo sessions.
    if "connection_count" in submission:
        return submission.get("connection_count", 0)
    connections = submission.get("connections")
    if isinstance(connections, dict):
        return sum(bool(value) for value in connections.values())
    return 0


def _document_count(submission, snapshot):
    # Document counts may live on the submission record or on older snapshots.
    # Keep both paths so restored sessions still render correctly.
    if "document_count" in submission:
        return submission.get("document_count", 0)
    documents = submission.get("documents")
    if isinstance(documents, list):
        return len(documents)
    return snapshot.get("stored_document_count", 0)


def submission_snapshot(submission, active_application=None, sme_application=None):
    """Return the best available application snapshot for a submitted SME file."""
    snapshot = submission.get("application_snapshot")
    if isinstance(snapshot, dict) and snapshot:
        # Prefer the immutable submitted copy; fallbacks support older demo sessions.
        return dict(snapshot)

    application_id = submission.get("application_id")
    for candidate in (active_application, sme_application):
        if (
            isinstance(candidate, dict)
            and candidate.get("application_id") == application_id
        ):
            return dict(candidate)
    return {}


def submitted_intake_rows(
    submissions, lifecycles, active_application=None, sme_application=None
):
    # Build lightweight queue rows for Home and Personal Workspace. The rows are
    # display summaries only; the full immutable application snapshot is loaded
    # separately when the analyst opens the case.
    rows = []
    for submission in submissions or []:
        # Merge lifecycle status into the queue row so lender pages show publication progress.
        application_id = submission.get("application_id")
        lifecycle = dict((lifecycles or {}).get(application_id, {}))
        snapshot = submission_snapshot(submission, active_application, sme_application)
        rows.append(
            {
                "Submission ID": submission.get("submission_id", ""),
                "Application ID": application_id,
                "Company": submission.get("company_name")
                or snapshot.get("company_name", "Applicant"),
                "Submitted": submission.get("timestamp")
                or submission.get("submitted_at", ""),
                "Status": lifecycle.get("status")
                or submission.get("status", "Submitted to lender review"),
                "Connections": f"{_connection_count(submission)}/4",
                "Documents": _document_count(submission, snapshot),
                "Published rating": lifecycle.get("published_grade", "Not published"),
            }
        )
    return rows


def find_submitted_application(
    submissions, application_id, active_application=None, sme_application=None
):
    # Walk newest first because the SME can resubmit the same application during a demo.
    for submission in reversed(submissions or []):
        if submission.get("application_id") == application_id:
            return submission_snapshot(submission, active_application, sme_application)
    return {}
