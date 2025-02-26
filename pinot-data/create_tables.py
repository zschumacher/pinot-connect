import json
import os
import pathlib
import time

import httpx

TABLE_TYPE = "OFFLINE"
HOST = os.getenv("PINOT_HOST", "localhost")
print(f"Connection to {HOST}")

AUTH = httpx.BasicAuth("admin", "verysecret")


def create_schema(schema_file_path: pathlib.Path):
    r = httpx.post(
        f"http://{HOST}:9000/schemas",
        auth=AUTH,
        json=json.load(schema_file_path.open()),
    )
    r.raise_for_status()


def create_table(tables_file_path: pathlib.Path):
    payload = json.load(tables_file_path.open())
    tries = 0
    while tries < 10:
        r = httpx.post(f"http://{HOST}:9000/tables", auth=AUTH, json=payload)
        if r.status_code == 400:
            print(r.json())
            print("Table creation not ready - retrying...")
            tries += 1
            time.sleep(0.5 * tries)
        elif r.status_code == 409:
            print("Table already exists!")
            return
        else:
            r.raise_for_status()
            return


def delete_table(tablename: str):
    r = httpx.delete(f"http://{HOST}/tables/{tablename}", auth=AUTH, params={"type": TABLE_TYPE})
    if r.status_code != 404:
        r.raise_for_status()


def load_data_from_file(table_name_with_type: str, file_path: pathlib.Path):
    fp = file_path.open("rb")
    r = httpx.post(
        f"http://{HOST}:9000/ingestFromFile",
        auth=AUTH,
        params={
            "tableNameWithType": table_name_with_type,
            "batchConfigMapStr": json.dumps(
                {
                    "inputFormat": "csv",
                    "record.prop.delimiter": ",",
                    "record.prop.header": "true",
                }
            ),
        },
        files={"file": (file_path.name, fp, "text/csv")},
    )
    fp.close()
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(r.json())
        raise


def check_table_can_be_queried(table_name: str):
    retries = 0
    while retries < 10:
        r = httpx.post(
            f"http://{HOST}:8099/query/sql",
            auth=AUTH,
            json={"sql": f"select * from {table_name}"},
        )
        if r.status_code == 400:
            print(f"{table_name} not ready - retrying...")
            retries += 1
            time.sleep(0.5 * retries)
        else:
            break


if __name__ == "__main__":
    pinot_path = pathlib.Path(__file__).parent

    print("Creating owner schema...")
    create_schema(pinot_path / "task_owner_schema.json")
    print("Creating task schema...")
    create_schema(pinot_path / "task_schema.json")

    print("Creating owner table...")
    create_table(pinot_path / "task_owner_table.json")
    print("Creating task table...")
    create_table(pinot_path / "task_table.json")
