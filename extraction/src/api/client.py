from __future__ import annotations

from typing import Any

import requests

from extraction.src.common.config import ConfigManager
from extraction.src.common.exceptions import FHIRAPIError
from extraction.src.common.logger import get_logger
from extraction.src.api.retry import fhir_retry
from extraction.src.api.auth import AuthManager

logger = get_logger(__name__)


class FHIRClient:
    """
    Generic client for calling FHIR REST APIs.
    """

    def __init__(self) -> None:

        self.config = ConfigManager()

        self.base_url: str = self.config.get("fhir.base_url")
        self.page_size: int = self.config.get("fhir.page_size")
        self.timeout: int = self.config.get("fhir.timeout_seconds")

        self.session = AuthManager.configure(
    requests.Session()
)

    @fhir_retry
    def get_resource(
        self,
        resource: str,
        last_updated: str | None = None,
        page_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch a single page of a FHIR resource.
        """

        url = page_url or f"{self.base_url}/{resource}"

        params: dict[str, Any] = {}

        if page_url is None:

            params["_count"] = self.page_size
            params["_sort"] = "_lastUpdated"

            if last_updated:
                params["_lastUpdated"] = f"gt{last_updated}"

        logger.info(f"Calling FHIR API: {url}")

        try:

            response = self.session.get(
                url=url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:

            logger.exception("FHIR API request failed.")

            raise FHIRAPIError(str(e)) from e