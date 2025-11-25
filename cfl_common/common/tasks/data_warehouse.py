"""
© Ocado Group
Created on 06/10/2025 at 17:15:37(+01:00).
"""

import csv
import io
import logging
import typing as t
from dataclasses import dataclass
from datetime import date, datetime, time, timezone

from celery import Task
from celery import shared_task as _shared_task
from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from google.auth import default, impersonated_credentials
from google.cloud import storage as gcs  # type: ignore[import-untyped]
from google.oauth2 import service_account

from .utils import get_task_name

_BQ_TABLE_NAMES: t.Set[str] = set()


# pylint: disable-next=abstract-method
class DataWarehouseTask(Task):
    """A task that saves a queryset as CSV files in the GCS bucket."""

    timestamp_key = "_timestamp"

    GetQuerySet: t.TypeAlias = t.Callable[..., QuerySet[t.Any]]
    BqTableWriteMode: t.TypeAlias = t.Literal["overwrite", "append"]

    # pylint: disable-next=too-many-instance-attributes
    class Settings:
        """The settings for a data warehouse task."""

        # pylint: disable-next=too-many-arguments,too-many-branches
        def __init__(
            self,
            bq_table_write_mode: "DataWarehouseTask.BqTableWriteMode",
            chunk_size: int,
            fields: t.List[str],
            id_field: str = "id",
            time_limit: int = 3600,
            bq_table_name: t.Optional[str] = None,
            max_retries: int = 5,
            retry_countdown: int = 10,
            **kwargs,
        ):
            # pylint: disable=line-too-long
            """Create the settings for a data warehouse task.

            Args:
                bq_table_write_mode: The BigQuery table's write-mode.
                chunk_size: The number of objects/rows per CSV. Must be a multiple of 10.
                fields: The [Django model] fields to include in the CSV.
                id_field: The name of the field used to identify each object.
                time_limit: The maximum amount of time this task is allowed to take before it's hard-killed.
                bq_table_name: The name of the BigQuery table where these CSV files will ultimately be imported into. If not provided, the name of the decorated function will be used instead.
                max_retries: The maximum number of retries allowed.
                retry_countdown: The countdown before attempting the next retry.
            """
            # pylint: enable=line-too-long

            # Set required values as defaults.
            kwargs.setdefault("bind", True)
            kwargs.setdefault("base", DataWarehouseTask)

            # Ensure the ID field is always present.
            if id_field not in fields:
                fields.append(id_field)

            # Validate args.
            if chunk_size <= 0:
                raise ValidationError(
                    "The chunk size must be > 0.",
                    code="chunk_size_lte_0",
                )
            if chunk_size % 10 != 0:
                raise ValidationError(
                    "The chunk size must be a multiple of 10.",
                    code="chunk_size_not_multiple_of_10",
                )
            if len(fields) <= 1:
                raise ValidationError(
                    "Must provide at least 1 field (not including ID field).",
                    code="no_fields",
                )
            if len(fields) != len(set(fields)):
                raise ValidationError(
                    "Fields must be unique.",
                    code="duplicate_fields",
                )
            if time_limit <= 0:
                raise ValidationError(
                    "The time limit must be > 0.",
                    code="time_limit_lte_0",
                )
            if time_limit > 3600:
                raise ValidationError(
                    "The time limit must be <= 3600 (1 hour).",
                    code="time_limit_gt_3600",
                )
            if max_retries < 0:
                raise ValidationError(
                    "The max retries must be >= 0.",
                    code="max_retries_lt_0",
                )
            if retry_countdown < 0:
                raise ValidationError(
                    "The retry countdown must be >= 0.",
                    code="retry_countdown_lt_0",
                )
            if kwargs["bind"] is not True:
                raise ValidationError(
                    "The task must be bound.", code="task_unbound"
                )
            if not issubclass(kwargs["base"], DataWarehouseTask):
                raise ValidationError(
                    f"The base must be a subclass of "
                    f"'{DataWarehouseTask.__module__}."
                    f"{DataWarehouseTask.__qualname__}'.",
                    code="base_not_subclass",
                )

            self._bq_table_write_mode = bq_table_write_mode
            self._chunk_size = chunk_size
            self._fields = fields
            self._id_field = id_field
            self._time_limit = time_limit
            self._bq_table_name = bq_table_name
            self._max_retries = max_retries
            self._retry_countdown = retry_countdown
            self._kwargs = kwargs

            # Get the runtime settings based on the BigQuery table's write-mode.
            bq_table_write_mode_is_append = bq_table_write_mode == "append"
            self._only_list_blobs_from_current_timestamp = (
                bq_table_write_mode_is_append
            )
            self._delete_blobs_not_from_current_timestamp = (
                not bq_table_write_mode_is_append
            )

        @property
        def bq_table_write_mode(self):
            """The BigQuery table's write-mode."""
            return self._bq_table_write_mode

        @property
        def chunk_size(self):
            """The number of objects/rows per CSV. Must be a multiple of 10."""
            return self._chunk_size

        @property
        def fields(self):
            """The [Django model] fields to include in the CSV."""
            return self._fields

        @property
        def id_field(self):
            """The name of the field used to identify each object."""
            return self._id_field

        @property
        def time_limit(self):
            """
            The maximum amount of time this task is allowed to take before it's
            hard-killed.
            """
            return self._time_limit

        @property
        def bq_table_name(self):
            """
            The name of the BigQuery table where the CSV files will ultimately
            be imported into.
            """
            return self._bq_table_name

        @property
        def max_retries(self):
            """The maximum number of retries allowed."""
            return self._max_retries

        @property
        def retry_countdown(self):
            """The countdown before attempting the next retry."""
            return self._retry_countdown

        @property
        def only_list_blobs_from_current_timestamp(self):
            """Whether to only list blobs from the current timestamp."""
            return self._only_list_blobs_from_current_timestamp

        @property
        def delete_blobs_not_from_current_timestamp(self):
            """Whether to delete all blobs not from the current timestamp."""
            return self._delete_blobs_not_from_current_timestamp

    settings: Settings
    get_queryset: GetQuerySet

    @dataclass
    class ChunkMetadata:
        """All of the metadata used to track a chunk."""

        bq_table_name: str  # the name of the BigQuery table
        bq_table_write_mode: "DataWarehouseTask.BqTableWriteMode"
        timestamp: str  # when the task was first run
        obj_i_start: int  # object index span start
        obj_i_end: int  # object index span end

        def to_blob_name(self):
            """Convert this chunk metadata into a blob name."""

            # E.g. "user__append/2025-01-01_00:00:00__1_1000.csv"
            return (
                f"{self.bq_table_name}__{self.bq_table_write_mode}/"
                f"{self.timestamp}__{self.obj_i_start}_{self.obj_i_end}.csv"
            )

        @classmethod
        def from_blob_name(cls, blob_name: str):
            """Extract the chunk metadata from a blob name."""

            # E.g. "user__append/2025-01-01_00:00:00__1_1000.csv"
            # "user__append", "2025-01-01_00:00:00__1_1000.csv"
            dir_name, file_name = blob_name.split("/")
            # "user", "append"
            bq_table_name, bq_table_write_mode = dir_name.rsplit(
                "__", maxsplit=1
            )
            assert bq_table_write_mode in ("overwrite", "append")
            # "2025-01-01_00:00:00__1_1000"
            file_name = file_name.removesuffix(".csv")
            # "2025-01-01_00:00:00", "1_1000"
            timestamp, obj_i_span = file_name.split("__")
            # "1", "1000"
            obj_i_start, obj_i_end = obj_i_span.split("_")

            return cls(
                bq_table_name=bq_table_name,
                bq_table_write_mode=t.cast(
                    DataWarehouseTask.BqTableWriteMode, bq_table_write_mode
                ),
                timestamp=timestamp,
                obj_i_start=int(obj_i_start),
                obj_i_end=int(obj_i_end),
            )

    def _get_gcs_bucket(self):
        # Set the scopes of the credentials.
        # https://cloud.google.com/storage/docs/oauth-scopes
        scopes = ["https://www.googleapis.com/auth/devstorage.full_control"]

        if django_settings.ENV == "local":
            # Load the credentials from a local JSON file.
            credentials = service_account.Credentials.from_service_account_file(
                "/replace/me/with/path/to/service_account.json",
                scopes=scopes,
            )
        else:
            # Use Workload Identity Federation to get the default credentials
            # from the environment. These are the short-lived credentials from
            # the AWS IAM role.
            source_credentials, _ = default()

            # Create the impersonated credentials object
            credentials = impersonated_credentials.Credentials(
                source_credentials=source_credentials,
                target_principal=(
                    django_settings.GOOGLE_CLOUD_STORAGE_SERVICE_ACCOUNT_NAME
                ),
                target_scopes=scopes,
                # The lifetime of the impersonated credentials in seconds.
                lifetime=self.settings.time_limit,
            )

        # Create a client with the impersonated credentials and get the bucket.
        return gcs.Client(credentials=credentials).bucket(
            django_settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME
        )

    def init_csv_writer(self):
        """Initializes a CSV writer.

        Returns:
            A tuple where the first value is the string buffer containing the
            CSV content and the second value is a CSV writer which handles
            writing new rows to the CSV buffer.
        """
        csv_content = io.StringIO()
        csv_writer = csv.writer(
            csv_content, lineterminator="\n", quoting=csv.QUOTE_MINIMAL
        )
        csv_writer.writerow(self.settings.fields)  # Write the headers.
        return csv_content, csv_writer

    @staticmethod
    def write_csv_row(
        writer: "csv.Writer",  # type: ignore[name-defined]
        values: t.Tuple[t.Any, ...],
    ):
        """Write the values to the CSV file in a format BigQuery accepts.

        Args:
            writer: The CSV writer which handles formatting the row.
            values: The values to write to the CSV file.
        """
        # Reimport required to avoid being mocked during testing.
        # pylint: disable-next=reimported,import-outside-toplevel
        from datetime import datetime as _datetime

        # Transform the values into their SQL representations.
        csv_row: t.List[str] = []
        for value in values:
            if value is None:
                value = ""  # BigQuery treats an empty string as NULL/None.
            elif isinstance(value, _datetime):
                value = (
                    value.astimezone(timezone.utc)
                    .replace(tzinfo=None)
                    .isoformat(sep=" ")
                )
            elif isinstance(value, (date, time)):
                value = value.isoformat()
            elif not isinstance(value, str):
                value = str(value)

            csv_row.append(value)

        writer.writerow(csv_row)

    @staticmethod
    def to_timestamp(dt: datetime):
        """
        Formats a datetime to a timestamp to be used in a CSV name.
        E.g. "2025-01-01_00:00:00"
        """
        return dt.strftime("%Y-%m-%d_%H:%M:%S")

    @staticmethod
    # pylint: disable-next=too-many-locals,bad-staticmethod-argument
    def _save_query_set_as_csvs_in_gcs_bucket(
        self: "DataWarehouseTask", timestamp: str, *task_args, **task_kwargs
    ):
        # Get the queryset.
        queryset = self.get_queryset(*task_args, **task_kwargs)

        # Count the objects in the queryset and ensure there's at least 1.
        obj_count = queryset.count()
        if obj_count == 0:
            return

        # If the queryset is not ordered, order it by ID by default.
        if not queryset.ordered:
            queryset = queryset.order_by(self.settings.id_field)

        # Limit the queryset to the object count to ensure the number of
        # digits in the count remains consistent.
        queryset = queryset[:obj_count]

        # Impersonate the service account and get access to the GCS bucket.
        bucket = self._get_gcs_bucket()

        # The name of the last blob from the current timestamp.
        last_blob_name_from_current_timestamp: t.Optional[str] = None

        # The name of the directory where the blobs are expected to be located.
        blob_dir_name = (
            f"{self.settings.bq_table_name}__"
            f"{self.settings.bq_table_write_mode}/"
        )

        # List all the existing blobs.
        for blob in t.cast(
            t.Iterator[gcs.Blob],
            bucket.list_blobs(
                prefix=blob_dir_name
                + (
                    timestamp
                    if self.settings.only_list_blobs_from_current_timestamp
                    else ""
                )
            ),
        ):
            blob_name = t.cast(str, blob.name)

            # Check if found first blob from current timestamp.
            if (
                self.settings.only_list_blobs_from_current_timestamp
                or blob_name.startswith(blob_dir_name + timestamp)
            ):
                last_blob_name_from_current_timestamp = blob_name
            # Check if blobs not from the current timestamp should be deleted.
            elif self.settings.delete_blobs_not_from_current_timestamp:
                logging.info('Deleting blob "%s".', blob_name)
                blob.delete()

        # Track the current and starting object index (1-based).
        obj_i = obj_i_start = (
            # ...extract the starting object index from its name.
            self.ChunkMetadata.from_blob_name(
                last_blob_name_from_current_timestamp
            ).obj_i_end
            + 1
            # If found a blob from the current timestamp...
            if last_blob_name_from_current_timestamp is not None
            else 1  # ...else start with the 1st object.
        )

        # If the queryset is not starting with the first object...
        if obj_i != 1:
            # ...offset the queryset...
            offset = obj_i - 1
            logging.info("Offsetting queryset by %d objects.", offset)
            queryset = queryset[offset:]

            # ...and ensure there's at least 1 object.
            if not queryset.exists():
                return

        chunk_i = obj_i // self.settings.chunk_size  # Chunk index (0-based).

        # Track content of the current CSV file.
        csv_content, csv_writer = self.init_csv_writer()

        # Uploads the current CSV file to the GCS bucket.
        def upload_csv(obj_i_end: int):
            # Calculate the starting object index for the current chunk.
            obj_i_start = (chunk_i * self.settings.chunk_size) + 1

            # Generate the path to the CSV in the bucket.
            blob_name = self.ChunkMetadata(
                bq_table_name=self.settings.bq_table_name,
                bq_table_write_mode=self.settings.bq_table_write_mode,
                timestamp=timestamp,
                obj_i_start=obj_i_start,
                obj_i_end=obj_i_end,
            ).to_blob_name()

            # Create a blob object for the CSV file's path and upload it.
            logging.info("Uploading %s to bucket.", blob_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(
                csv_content.getvalue().strip(), content_type="text/csv"
            )

        # Iterate through the all the objects in the queryset. The objects
        # are retrieved in chunks (no caching) to avoid OOM errors. For each
        # object, a tuple of values is returned. The order of the values in
        # the tuple is determined by the order of the fields.
        for obj_i, values in enumerate(
            t.cast(
                t.Iterator[t.Tuple[t.Any, ...]],
                queryset.values_list(*self.settings.fields).iterator(
                    chunk_size=self.settings.chunk_size
                ),
            ),
            start=obj_i_start,
        ):
            if obj_i % self.settings.chunk_size == 1:  # If start of a chunk...
                if obj_i != obj_i_start:  # ...and not the 1st iteration...
                    # ...upload the chunk's CSV and increment its index...
                    upload_csv(obj_i_end=obj_i - 1)
                    chunk_i += 1

                # ...and start a new CSV.
                csv_content, csv_writer = self.init_csv_writer()

            self.write_csv_row(csv_writer, values)

        upload_csv(obj_i_end=obj_i)  # Upload final (maybe partial) chunk.

    @classmethod
    def shared(cls, settings: Settings):
        # pylint: disable=line-too-long,anomalous-backslash-in-string
        """Create a Celery task that saves a queryset as CSV files in the GCS
        bucket.

        This decorator handles chunking a queryset to avoid out-of-memory (OOM)
        errors. Each chunk is saved as a separate CSV file and follows a naming
        convention that tracks 2 dimensions:

        1. timestamp - When this task first ran (in case of retries).
        2. object index (obj_i) - The start and end index of the objects.

        The naming convention follows the format:
            `{timestamp}__{i_start}_{i_end}.csv`
        The timestamp follows the format:
            `{YYYY}-{MM}-{DD}_{HH}:{MM}:{SS}` (e.g. `2025-12-01_23:59:59`)

        NOTE: The index is padded with zeros to ensure sorting by name is
        consistent. For example, the index span from 1 to 500 would be
        `001_500`.

        Ultimately, these CSV files are imported into a BigQuery table, after
        which they are deleted from the GCS bucket.

        Each task *must* be given a distinct table name and queryset to avoid
        unintended consequences.

        Examples:
            ```
            @DataWarehouseTask.shared(
                DataWarehouseTask.Options(
                    # bq_table_name = "example", <- Alternatively, set the table name like so.
                    bq_table_write_mode="append",
                    chunk_size=1000,
                    fields=["first_name", "joined_at", "is_active"],
                )
            )
            def user(): # CSVs will be saved to a BQ table named "user"
                return User.objects.all()
            ```

        Args:
            settings: The settings for this data warehouse task.

        Returns:
            A wrapper-function which expects to receive a callable that returns
            a queryset and returns a Celery task to save the queryset as CSV
            files in the GCS bucket.
        """
        # pylint: enable=line-too-long,anomalous-backslash-in-string

        def wrapper(get_queryset: "DataWarehouseTask.GetQuerySet"):
            # Get BigQuery table name and validate it's not already registered.
            bq_table_name = settings.bq_table_name or get_queryset.__name__
            if bq_table_name in _BQ_TABLE_NAMES:
                raise ValueError(
                    f'The BigQuery table name "{bq_table_name}" is already'
                    "registered."
                )
            _BQ_TABLE_NAMES.add(bq_table_name)

            # Overwrite BigQuery table name.
            # pylint: disable-next=protected-access
            settings._bq_table_name = bq_table_name

            # Wraps the task with retry logic.
            def task(self: "DataWarehouseTask", *task_args, **task_kwargs):
                # If this is not the first run...
                if self.request.retries:
                    # ...pop the timestamp passed from the first run.
                    timestamp = t.cast(str, task_kwargs.pop(self.timestamp_key))
                else:  # ...else get the current timestamp.
                    timestamp = self.to_timestamp(datetime.now(timezone.utc))

                try:
                    cls._save_query_set_as_csvs_in_gcs_bucket(
                        self, timestamp, *task_args, **task_kwargs
                    )
                except Exception as exc:
                    # Pass the timestamp to the retry.
                    task_kwargs[self.timestamp_key] = timestamp

                    raise self.retry(
                        args=task_args,
                        kwargs=task_kwargs,
                        exc=exc,
                        countdown=settings.retry_countdown,
                    )

            # pylint: disable-next=protected-access
            kwargs = settings._kwargs

            # Namespace the task with service's name. If the name is not
            # explicitly provided, it defaults to the name of the decorated
            # function.
            name = kwargs.pop("name", None)
            name = get_task_name(
                name if isinstance(name, str) else get_queryset
            )

            return t.cast(
                DataWarehouseTask,
                _shared_task(  # type: ignore[call-overload]
                    **kwargs,
                    name=name,
                    time_limit=settings.time_limit,
                    max_retries=settings.max_retries,
                    settings=settings,
                    get_queryset=staticmethod(get_queryset),
                )(task),
            )

        return wrapper
