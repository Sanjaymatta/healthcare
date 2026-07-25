from __future__ import annotations

from requests import Session

from src.common.logger import get_logger

logger = get_logger(__name__)


class AuthManager:
    """
    Handles authentication for FHIR API requests.

    Currently, authentication is not required.
    This class exists to support future authentication methods
    such as OAuth2, Bearer Token, API Key, etc.
    """

    @staticmethod
    def configure(session: Session) -> Session:
        """
        Configure authentication for the HTTP session.
        """

        logger.info("Authentication is not required.")

        return session