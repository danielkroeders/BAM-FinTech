SME_SUBMISSION_SOURCE = "SME Portal submission"


def _connection_count(submission):
    if "connection_count" in submission:
        return submission.get("connection_count", 0)
    connections = submission.get("connections")
    if isinstance(connections, dict):
        return sum(bool(value) for value in connections.values())
    return 0


def _document_count(submission, snapshot):
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
    rows = []
    for submission in submissions or []:
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
    for submission in reversed(submissions or []):
        if submission.get("application_id") == application_id:
            return submission_snapshot(submission, active_application, sme_application)
    return {}
