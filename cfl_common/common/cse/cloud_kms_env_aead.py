import logging
from typing import Optional

import tink
from google.cloud import kms_v1
from google.oauth2 import service_account
from tink import aead
from tink import aead
from tink.integration import gcpkms

logger = logging.getLogger(__name__)


def init_tink_env_aead(
    key_uri: str, credentials: str
) -> tink.aead.KmsEnvelopeAead:
    """
    Initiates the Envelope AEAD object using the KMS credentials.
    """
    aead.register()

    try:
        gcp_client = GcpKmsClient(key_uri, credentials)
        gcp_aead = gcp_client.get_aead(key_uri)
    except tink.TinkError as e:
        logger.error("Error initializing GCP client: %s", e)
        raise e

    # Create envelope AEAD primitive using AES256 GCM for encrypting the data
    # This key should only be used for client-side encryption to ensure authenticity and integrity
    # of data.
    key_template = aead.aead_key_templates.AES256_GCM
    env_aead = aead.KmsEnvelopeAead(key_template, gcp_aead)

    print(f"Created envelope AEAD Primitive using KMS URI: {key_uri}")

    return env_aead


class GcpKmsClient(tink.KmsClient):
    """Basic GCP client for AEAD."""

    def __init__(
            self, key_uri: Optional[str], credentials_dict: Optional[str]
    ) -> None:
        """Creates a new GcpKmsClient that is bound to the key specified in 'key_uri'.

        Uses the specified credentials when communicating with the KMS.

        Args:
          key_uri: The URI of the key the client should be bound to. If it is None
              or empty, then the client is not bound to any particular key.
          credentials_path: Path to the file with the access credentials. If it is
              None or empty, then default credentials will be used.

        Raises:
          ValueError: If the path or filename of the credentials is invalid.
          TinkError: If the key uri is not valid.
        """

        if not key_uri:
            self._key_uri = None
        elif key_uri.startswith('gcp-kms://'):
            self._key_uri = key_uri
        else:
            raise tink.TinkError('Invalid key_uri.')
        # if not credentials_path:
        #     credentials_path = ''
        # if not credentials_path:
        #     self._client = kms_v1.KeyManagementServiceClient()
        #     return

        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict
        )
        self._client = kms_v1.KeyManagementServiceClient(credentials=credentials)
