from __future__ import annotations

from src.common.logger import get_logger

logger = get_logger(__name__)


class CheckpointManager:
    """
    Manages extraction checkpoints.

    Currently uses an in-memory placeholder.
    Later this will be replaced with Snowflake.
    """

    def __init__(self) -> None:
        pass

    def get_checkpoint(
        self,
        resource_name: str,
    ) -> str | None:
        """
        Return the last successful checkpoint for a resource.

        Returns:
            ISO-8601 timestamp or None for first load.
        """

        logger.info(
            f"Fetching checkpoint for resource: {resource_name}"
        )

        # TODO:
        # Replace with Snowflake query.
        checkpoint = None

        if checkpoint is None:
            logger.info(
                f"No checkpoint found for {resource_name}. "
                "Starting full extraction."
            )
        else:
            logger.info(
                f"Checkpoint found: {checkpoint}"
            )

        return checkpoint