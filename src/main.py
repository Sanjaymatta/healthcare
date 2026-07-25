from __future__ import annotations

import argparse
import sys
import uuid

from src.common.logger import get_logger
from src.extractors.resource_extractor import ResourceExtractor

logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description="FHIR Resource Extraction"
    )

    parser.add_argument(
        "--resource",
        required=True,
        help="FHIR Resource Name",
    )

    parser.add_argument(
        "--s3-prefix",
        required=True,
        help="S3 Prefix",
    )

    parser.add_argument(
        "--run-id",
        default=str(uuid.uuid4()),
        help="Pipeline Run ID",
    )

    return parser.parse_args()


def main() -> int:

    args = parse_arguments()

    logger.info("FHIR Extraction Started")

    try:

        extractor = ResourceExtractor()

        result = extractor.extract(
            resource_name=args.resource,
            run_id=args.run_id,
            s3_prefix=args.s3_prefix,
        )

        logger.info("Extraction Completed Successfully")

        logger.info(result)

        return 0

    except Exception:

        logger.exception("FHIR Extraction Failed")

        return 1


if __name__ == "__main__":
    sys.exit(main())