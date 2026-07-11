class FHIRFrameworkException(Exception):
    """
    Base exception for the Healthcare FHIR Ingestion Framework.
    """


class ConfigurationError(FHIRFrameworkException):
    """
    Raised when application configuration is invalid or missing.
    """


class FHIRAPIError(FHIRFrameworkException):
    """
    Raised for FHIR API related failures.
    """


class StorageError(FHIRFrameworkException):
    """
    Raised for S3 storage related failures.
    """


class CheckpointError(FHIRFrameworkException):
    """
    Raised when checkpoint operations fail.
    """


class AuditError(FHIRFrameworkException):
    """
    Raised when audit operations fail.
    """


class SnowflakeError(FHIRFrameworkException):
    """
    Raised for Snowflake related failures.
    """