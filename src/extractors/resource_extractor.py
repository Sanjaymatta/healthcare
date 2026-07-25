from __future__ import annotations

from datetime import datetime
from queue import Queue
from threading import Event

from src.api.client import FHIRClient
from src.api.paginator import FHIRPaginator
from src.common.logger import get_logger
from src.extractors.result import ExtractionResult
from src.extractors.worker import UploadTask, UploadWorker
from src.storage.s3_client import S3Client

logger = get_logger(__name__)


class ResourceExtractor:

    def __init__(self) -> None:

        self.client = FHIRClient()
        
        self.s3_client = S3Client()

    def extract(
        self,
        resource_name: str,
        last_updated: str | None,
        run_id: str,
        s3_prefix: str,
    ) -> ExtractionResult:

        logger.info(
            f"Starting extraction for resource: {resource_name}"
        )

        start_time = datetime.utcnow()

        run_folder = start_time.strftime("%Y%m%d_%H%M%S")

        
        upload_queue: Queue[UploadTask] = Queue()

        stop_event = Event()

        worker = UploadWorker(
            upload_queue=upload_queue,
            stop_event=stop_event,
            s3_client=self.s3_client,
        )

        worker.start()

        total_records = 0
        total_pages = 0
        files_uploaded = 0
        max_last_updated = None

        next_page = None

        try:

            while True:

                bundle = self.client.get_resource(
                    resource=resource_name,
                    last_updated=last_updated,
                    page_url=next_page,
                )

                entries = bundle.get("entry", [])

                if not entries:
                    break

                total_pages += 1
                total_records += len(entries)

                last_resource = entries[-1].get("resource")

                if last_resource:

                    current_last_updated = (
                        last_resource
                        .get("meta", {})
                        .get("lastUpdated")
                    )

                    if (
                        current_last_updated
                        and (
                            max_last_updated is None
                            or current_last_updated > max_last_updated
                        )
                    ):
                        max_last_updated = current_last_updated

            

                s3_key = (
                f"{s3_prefix}/"
                f"{resource_name}/"
                f"{run_folder}/"
                f"{resource_name}_page_{total_pages:05}.json"
                )

                upload_queue.put(
                    UploadTask(
                        resource_name=resource_name,
                        page_number=total_pages,
                        bundle=bundle,
                        s3_key=s3_key,
                    )
                )

                files_uploaded += 1

                next_page = FHIRPaginator.get_next_page(bundle)

                if next_page is None:
                    break

        finally:
            upload_queue.join()

            stop_event.set()

            worker.join()

        end_time = datetime.utcnow()

        logger.info(
            "Extraction completed for resource: %s",
            resource_name,
        )

        logger.info(
            "Pages Processed: %s | Records Extracted: %s | Files Uploaded: %s",
            total_pages,
            total_records,
            files_uploaded,
        )

        result = ExtractionResult(
            resource_name=resource_name,
            run_id=run_id,
            records_extracted=total_records,
            pages_processed=total_pages,
            files_uploaded=files_uploaded,
            s3_prefix=s3_prefix,
            max_last_updated=max_last_updated,
            started_at=start_time,
            completed_at=end_time,
        )

        metadata_key = (
            f"{s3_prefix}/"
            f"{resource_name}/"
            f"{run_folder}/"
            "_metadata.json"
        )

        self.s3_client.upload_metadata(
            result=result,
            s3_key=metadata_key,
        )


        return result

        # return ExtractionResult(
        #     resource_name=resource_name,
        #     run_id=run_id,
        #     records_extracted=total_records,
        #     pages_processed=total_pages,
        #     files_uploaded=files_uploaded,
        #     s3_prefix=s3_prefix,
        #     max_last_updated=max_last_updated,
        #     started_at=start_time,
        #     completed_at=end_time,
        # )