from io import BytesIO
from typing import Any

import boto3
import orjson
from botocore.exceptions import BotoCoreError, ClientError
from dataclasses import asdict
from extraction.src.common.config import ConfigManager
from extraction.src.common.exceptions import StorageError
from extraction.src.common.logger import get_logger

logger = get_logger(__name__)


class S3Client:

    def __init__(self) -> None:

        config = ConfigManager()

        self.bucket_name = config.get("aws.bucket_name")

        self.client = boto3.client(
            "s3",
            region_name=config.get("aws.region"),
        )

    def upload_metadata(
    self,
    result,
    s3_key: str,
    ) -> None:

        try:

            logger.info(f"Uploading metadata to {s3_key}")

            buffer = BytesIO(
                orjson.dumps(
                    asdict(result),
                    option=orjson.OPT_INDENT_2,
                )
            )

            self.client.upload_fileobj(
                Fileobj=buffer,
                Bucket=self.bucket_name,
                Key=s3_key,
            )

            logger.info("Metadata upload completed.")

        except (ClientError, BotoCoreError) as e:

            logger.exception("Metadata upload failed.")

            raise StorageError(str(e)) from e

    def upload_bundle(
        self,
        bundle: dict[str, Any],
        s3_key: str,
    ) -> None:

        try:

            logger.info(f"Uploading bundle to {s3_key}")

            buffer = BytesIO(
                orjson.dumps(bundle)
            )

            self.client.upload_fileobj(
                Fileobj=buffer,
                Bucket=self.bucket_name,
                Key=s3_key,
            )

            logger.info("Upload completed.")

        except (ClientError, BotoCoreError) as e:

            logger.exception("Upload failed.")

            raise StorageError(str(e)) from e