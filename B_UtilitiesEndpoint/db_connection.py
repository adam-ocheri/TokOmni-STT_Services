import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
postgres_db_name = os.getenv("POSTGRES_DB_NAME")
postgres_db_user = os.getenv("POSTGRES_DB_USER")
postgres_db_password = os.getenv("POSTGRES_DB_PASSWORD")
postgres_db_url = os.getenv("POSTGRES_DB_URL")
postgres_db_port = os.getenv("POSTGRES_DB_PORT")

# Replace these values with your AWS PostgreSQL connection details
database = postgres_db_name
port = postgres_db_port
user = postgres_db_user
password = postgres_db_password
host = postgres_db_url

table_name = "test_table"

def stringify_transcript(transcript):
    counter = 0
    stringified_transcript = ""
    for item in transcript:
        str_item = str(item).replace(
            "'", '"'
        )  # replace "" double quotes with single quotes
        comma = ", " if counter > 0 else ""
        stringified_transcript += comma + f"'{str_item}'::jsonb"
        counter += 1
    return f"{stringified_transcript}"


class PostgresController:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                host=host, port=port, database=database, user=user, password=password
            )
            self.cursor = self.connection.cursor()
            self.working_id = -1
        except Exception as e:
            print("Error constructing PostgresController object: ", e)

    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def on_transcription_requested(self):
        insert_query = (
            f"INSERT INTO {table_name} (status, data) VALUES"
            + """
            ('pending', ARRAY[]::jsonb[]) RETURNING id;
        """
        )
        self.cursor.execute(insert_query)
        self.connection.commit()
        self.working_id = self.cursor.fetchone()[0]

        # return inserted_id

    def on_transcription_finished(self, transcript):
        formatted_transcript = stringify_transcript(transcript)
        update_query = (
            f"UPDATE {table_name}"
            + f"""
            SET status = 'finished',
                data = ARRAY[{formatted_transcript}]
            WHERE id = {self.working_id};
        """
        )
        self.cursor.execute(update_query)
        self.connection.commit()
        self.working_id = -1

    def on_transcription_failed(self):
        update_query = (
            f"UPDATE {table_name}"
            + f"""
            SET status = 'failed'
            WHERE id = {self.working_id};  
        """
        )
        self.cursor.execute(update_query)
        self.connection.commit()
        self.working_id = -1
