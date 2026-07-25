from __future__ import annotations

from typing import Any


class FHIRPaginator:
    """
    Extracts pagination information from a FHIR Bundle.
    """

    @staticmethod
    def get_next_page(bundle: dict[str, Any]) -> str | None:
        """
        Returns the next page URL if available.
        """

        links = bundle.get("link", [])

        for link in links:
            if link.get("relation") == "next":
                return link.get("url")

        return None