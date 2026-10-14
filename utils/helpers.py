import clickhouse_connect
from clickhouse_connect.driver.exceptions import OperationalError
from dotenv import load_dotenv
import os


def get_clickhouse_client(database:str):
    load_dotenv()

    try:
        client = clickhouse_connect.get_client(
            host="localhost",
            port=os.getenv("CLICKHOUSE_HTTP_PORT"),
            user=os.getenv("CLICKHOUSE_USER"),
            password=os.getenv("CLICKHOUSE_PASSWORD"),
            connect_timeout=10,
            database=database
        )
        print("Connected to ClickHouse")
        return client
    except OperationalError as e:
        print(f"Error connecting to ClickHouse: {e}")
    