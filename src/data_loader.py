from utils.helpers import get_clickhouse_client
from clickhouse_connect.driver.tools import insert_file
from pathlib import Path
from clickhouse_connect.driver.exceptions import (
    OperationalError,
    DatabaseError,
    DataError,
)

datafile_path = Path("./dataset")

def load_csv_files():
    try:
        datafiles = datafile_path.glob("*.csv")
        with get_clickhouse_client(database="inventra") as client:
            for file in datafiles:
                print(f"Loading {file.name} into ClickHouse...")
                insert_file(
                    client,
                    table="raw_" + file.stem,
                    file_path= str(file),
                    fmt="CSVWithNames",
                )
                print(f"Successfully loaded {file.name} into ClickHouse.")

    except (OperationalError, DatabaseError, DataError) as e:
        print(f"Error loading data: {e}")



if __name__ == "__main__":
    load_csv_files()
