import os

import sqlalchemy
import tink

from .cloud_kms_env_aead import init_tink_env_aead
from .cloud_sql_connection_pool import init_db


def cse_setup() -> (tink.aead.KmsEnvelopeAead, sqlalchemy.engine.base.Engine):
    """
    Connects to the database, initialises Tink AEAD.
    """
    db_user = os.environ["DB_USER"]  # e.g. "root", "mysql"
    db_pass = os.environ["DB_PASS"]  # e.g. "mysupersecretpassword"
    db_name = os.environ["DB_NAME"]  # e.g. "votes_db"

    # Set if connecting using TCP:
    db_host = os.environ["DB_HOST"]  # e.g. "127.0.0.1"

    # Set if connecting using Unix sockets:
    db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")

    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    # e.g. "project-name:region:instance-name"

    credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    key_uri = "gcp-kms://" + os.environ["GCP_KMS_URI"]
    # e.g. "gcp-kms://projects/...path/to/key
    # Tink uses the "gcp-kms://" prefix for paths to keys stored in Google
    # Cloud KMS. For more info on creating a KMS key and getting its path, see
    # https://cloud.google.com/kms/docs/quickstart

    table_name = "votes"
    team = "TABS"
    email = "hello@example.com"

    env_aead = init_tink_env_aead(key_uri, credentials)
    db = init_db(
        db_user,
        db_pass,
        db_name,
        table_name,
        instance_connection_name,
        db_socket_dir,
        db_host,
    )

    return env_aead, db
