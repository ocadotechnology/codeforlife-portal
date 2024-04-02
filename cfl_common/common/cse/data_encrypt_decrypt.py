import datetime
import logging

import sqlalchemy
import tink

logger = logging.getLogger(__name__)


def encrypt_and_insert_data(
    db: sqlalchemy.engine.base.Engine,
    env_aead: tink.aead.KmsEnvelopeAead,
    table_name: str,
    team: str,
    email: str,
) -> None:
    """
    Inserts a vote into the database with email address previously encrypted using
    a KmsEnvelopeAead object.
    """
    time_cast = datetime.datetime.now(tz=datetime.timezone.utc)
    # Use the envelope AEAD primitive to encrypt the email, using the team name as
    # associated data. Encryption with associated data ensures authenticity
    # (who the sender is) and integrity (the data has not been tampered with) of that
    # data, but not its secrecy. (see RFC 5116 for more info)
    encrypted_email = env_aead.encrypt(email.encode(), team.encode())
    # Verify that the team is one of the allowed options
    if team != "TABS" and team != "SPACES":
        logger.error(f"Invalid team specified: {team}")
        return

    # Preparing a statement beforehand can help protect against injections.
    stmt = sqlalchemy.text(
        f"INSERT INTO {table_name} (time_cast, team, voter_email)"
        " VALUES (:time_cast, :team, :voter_email)"
    )

    # Using a with statement ensures that the connection is always released
    # back into the pool at the end of statement (even if an error occurs)
    with db.connect() as conn:
        conn.execute(
            stmt, time_cast=time_cast, team=team, voter_email=encrypted_email
        )
    print(f"Vote successfully cast for '{team}' at time {time_cast}!")


def query_and_decrypt_data(
    db: sqlalchemy.engine.base.Engine,
    env_aead: tink.aead.KmsEnvelopeAead,
    table_name: str,
) -> list[tuple[str]]:
    """
    Retrieves data from the database and decrypts it using the KmsEnvelopeAead object.
    """
    with db.connect() as conn:
        # Execute the query and fetch all results
        recent_votes = conn.execute(
            f"SELECT team, time_cast, voter_email FROM {table_name} "
            "ORDER BY time_cast DESC LIMIT 5"
        ).fetchall()

        print("Team\tEmail\tTime Cast")
        output = []

        for row in recent_votes:
            team = row[0]
            # Use the envelope AEAD primitive to decrypt the email, using the team name as
            # associated data. Encryption with associated data ensures authenticity
            # (who the sender is) and integrity (the data has not been tampered with) of that
            # data, but not its secrecy. (see RFC 5116 for more info)
            email = env_aead.decrypt(row[2], team.encode()).decode()
            time_cast = row[1]

            # Print recent votes
            print(f"{team}\t{email}\t{time_cast}")
            output.append((team, email, time_cast))
    return output
