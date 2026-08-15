from dataclasses import dataclass
from queue import Empty, Queue
from threading import Event, Thread
from typing import Any

from extraction.src.common.logger import get_logger
from extraction.src.storage.s3_client import S3Client

logger = get_logger(__name__)


@dataclass(slots=True)
class UploadTask:
    resource_name: str
    page_number: int
    bundle: dict[str, Any]
    s3_key: str


class UploadWorker(Thread):

    def __init__(
        self,
        upload_queue: Queue[UploadTask],
        stop_event: Event,
        s3_client: S3Client,
    ) -> None:

        super().__init__(daemon=True)

        self.upload_queue = upload_queue
        self.stop_event = stop_event
        self.s3_client = s3_client

    def run(self) -> None:

        logger.info("Upload worker started.")

        while True:

            try:
                task = self.upload_queue.get(timeout=1)

            except Empty:

                if self.stop_event.is_set():
                    logger.info("Upload worker stopped.")
                    break

                continue

            try:

                self.s3_client.upload_bundle(
                    bundle=task.bundle,
                    s3_key=task.s3_key,
                )

            finally:

                self.upload_queue.task_done()