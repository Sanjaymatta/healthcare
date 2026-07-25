from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ExtractionResult:
    """
    Summary of a resource extraction run.
    """

    resource_name: str
    run_id: str

    records_extracted: int
    pages_processed: int
    files_uploaded: int

    s3_prefix: str

    max_last_updated: str | None

    started_at: datetime
    completed_at: datetime