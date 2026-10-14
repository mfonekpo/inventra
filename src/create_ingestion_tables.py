#!/usr/bin/env python3
"""Validate source files, then preview or create raw ClickHouse tables."""

import argparse
import csv
import hashlib
import os
import re
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parents[1]
IDENTIFIER = re.compile(r"[a-z_][a-z0-9_]*")


class UniqueSafeLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError("YAML keys must be unique strings.")
        result[key] = loader.construct_object(value_node)
    return result


UniqueSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def read_yaml(path):
    with path.open(encoding="utf-8") as handle:
        value = yaml.load(handle, Loader=UniqueSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: expected a YAML mapping.")
    return value


def quote_identifier(name):
    if not isinstance(name, str) or not IDENTIFIER.fullmatch(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return f'"{name}"'


def require_count(value, label):
    if type(value) is not int or value < 0:
        raise ValueError(f"{label}: expected a nonnegative integer.")
    return value


def validate_sources(schema, manifest, manifest_path):
    if any(type(v) is not int or v != 1 for v in (
        schema.get("version"), manifest.get("version")
    )):
        raise ValueError("Both files must declare version: 1.")
    if schema.get("engine") != "MergeTree":
        raise ValueError("This script supports only MergeTree.")
    if manifest.get("kind") != "source_snapshot":
        raise ValueError("Expected a source_snapshot manifest.")
    if manifest.get("csv") != {
        "encoding": "utf-8", "delimiter": ",",
        "quotechar": '"', "has_header": True,
    }:
        raise ValueError("Expected UTF-8, comma-delimited CSV with a header.")

    quote_identifier(schema["database"])
    tables, files = schema["tables"], manifest["files"]
    if not isinstance(tables, dict) or not tables:
        raise ValueError("schema.tables must be a nonempty mapping.")
    if not isinstance(files, dict) or set(tables) != set(files):
        raise ValueError("Schema and manifest must cover identical sources.")
    ordering = schema.get("order_by")
    if not isinstance(ordering, dict) or set(ordering) != set(tables):
        raise ValueError("order_by must define keys for every source table.")
    root = (manifest_path.parent / manifest["source_root"]).resolve()
    if not root.is_dir():
        raise ValueError("The manifest source_root directory does not exist.")

    targets, filenames = set(), set()
    total_rows = total_bytes = 0

    for source, spec in tables.items():
        quote_identifier(source)
        target, columns = spec["target"], spec["columns"]
        quote_identifier(target)
        if target in targets:
            raise ValueError(f"Repeated destination table: {target}")
        targets.add(target)
        if not isinstance(columns, dict) or not columns:
            raise ValueError(f"{source}: missing columns.")
        for column, column_type in columns.items():
            quote_identifier(column)
            if column_type != "String":
                raise ValueError(f"{source}.{column}: raw type must be String.")

        keys = ordering[source]
        if not isinstance(keys, list) or not keys:
            raise ValueError(f"{source}: order_by must be a nonempty list.")

        for key in keys:
            quote_identifier(key)
            if key not in columns:
                raise ValueError(
                    f"{source}: unknown sorting column {key!r}."
                )

        if len(keys) != len(set(keys)):
            raise ValueError(f"{source}: sorting columns must be distinct.")

        spec["order_by"] = list(keys)
        item = files[source]
        filename = item["file"]
        if not isinstance(filename, str) or filename != f"{source}.csv":
            raise ValueError(f"{source}: expected filename {source}.csv.")
        if filename in filenames:
            raise ValueError(f"Repeated source filename: {filename}")
        filenames.add(filename)

        expected_rows = require_count(item["row_count"], filename)
        expected_bytes = require_count(item["size_bytes"], filename)
        width = require_count(item["column_count"], filename)
        if width != len(columns):
            raise ValueError(f"{filename}: column_count differs from schema.")
        if not isinstance(item["sha256"], str) or not re.fullmatch(
            r"[0-9a-f]{64}", item["sha256"]
        ):
            raise ValueError(f"{filename}: invalid SHA-256.")

        path = (root / filename).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"{filename}: missing or outside source_root.")

        digest = hashlib.sha256()
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        if before.st_size != expected_bytes or digest.hexdigest() != item["sha256"]:
            raise ValueError(f"{filename}: size/checksum mismatch.")

        rows = 0
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter=",", quotechar='"', strict=True)
            if next(reader, None) != list(columns):
                raise ValueError(f"{filename}: CSV header differs from schema.")
            for rows, row in enumerate(reader, start=1):
                if len(row) != width:
                    raise ValueError(f"{filename}: invalid width at record {rows}.")
            after = os.fstat(handle.fileno())
        if (before.st_dev, before.st_ino, before.st_size,
            before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_dev, after.st_ino, after.st_size,
            after.st_mtime_ns, after.st_ctime_ns
        ):
            raise ValueError(f"{filename}: changed during validation.")
        if rows != expected_rows:
            raise ValueError(f"{filename}: expected {expected_rows} rows; got {rows}.")

        total_rows += rows
        total_bytes += expected_bytes
        print(f"Verified {filename}: {rows:,} records.")

    if total_rows != require_count(manifest["total_rows"], "total_rows") or (
        total_bytes != require_count(manifest["total_bytes"], "total_bytes")
    ):
        raise ValueError("Manifest totals do not match the verified files.")
    return tables


def create_statement(database, spec):
    columns = ",\n    ".join(
        f"{quote_identifier(name)} String"
        for name in spec["columns"]
    )
    sorting_key = ", ".join(
        quote_identifier(name)
        for name in spec["order_by"]
    )
    return (
        f"CREATE TABLE IF NOT EXISTS {quote_identifier(database)}."
        f"{quote_identifier(spec['target'])} (\n    {columns}\n)"
        f"\nENGINE = MergeTree\nORDER BY ({sorting_key})"
    )


def normalize_key(expression):
    value = expression.replace("`", "").replace('"', "")
    value = re.sub(r"\s+", "", value)

    if value.startswith("tuple(") and value.endswith(")"):
        value = value[6:-1]
    elif value.startswith("(") and value.endswith(")"):
        value = value[1:-1]

    return tuple(value.split(",")) if value else ()


def check_existing(client, database, spec):
    params = {"db": database, "table": spec["target"]}

    objects = client.query(
        """
        SELECT
            engine,
            sorting_key,
            primary_key,
            partition_key,
            sampling_key
        FROM system.tables
        WHERE database = {db:String}
          AND name = {table:String}
        """,
        parameters=params,
    ).result_rows

    if not objects:
        return False

    engine, sorting, primary, partition, sampling = objects[0]
    expected_key = tuple(spec["order_by"])

    expected_metadata = {
        "engine": "MergeTree",
        "sorting_key": expected_key,
        "primary_key": expected_key,
        "partition_key": (),
        "sampling_key": "",
    }
    actual_metadata = {
        "engine": engine,
        "sorting_key": normalize_key(sorting),
        "primary_key": normalize_key(primary),
        "partition_key": normalize_key(partition),
        "sampling_key": sampling,
    }
    differences = [
        f"{field}: expected {expected!r}, found {actual_metadata[field]!r}"
        for field, expected in expected_metadata.items()
        if actual_metadata[field] != expected
    ]
    if differences:
        raise ValueError(
            f"{database}.{spec['target']}: existing engine/keys differ: "
            + "; ".join(differences)
            + ". CREATE TABLE IF NOT EXISTS does not update existing tables. "
            "Use an explicit, data-preserving migration before retrying."
        )

    actual = client.query(
        """
        SELECT name, type, default_kind, default_expression
        FROM system.columns
        WHERE database = {db:String}
          AND table = {table:String}
        ORDER BY position
        """,
        parameters=params,
    ).result_rows

    expected = [
        (name, "String", "", "")
        for name in spec["columns"]
    ]

    if [tuple(row) for row in actual] != expected:
        raise ValueError(
            f"{database}.{spec['target']}: existing column definitions differ."
        )

    return True


def connect(database):
    import clickhouse_connect
    from dotenv import load_dotenv

    load_dotenv(BASE / ".env", override=False)
    host = os.getenv("CLICKHOUSE_HOST", "localhost")
    secure_value = os.getenv("CLICKHOUSE_SECURE", "false").lower()
    if secure_value not in {"true", "false"}:
        raise ValueError("CLICKHOUSE_SECURE must be true or false.")
    secure = secure_value == "true"
    if not secure and host not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Use CLICKHOUSE_SECURE=true for a remote connection.")
    if os.getenv("CLICKHOUSE_DB", database) != database:
        raise ValueError("CLICKHOUSE_DB differs from schema.database.")

    user, password = os.getenv("CLICKHOUSE_USER"), os.getenv("CLICKHOUSE_PASSWORD")
    if not user or not password:
        raise ValueError("Set CLICKHOUSE_USER and CLICKHOUSE_PASSWORD.")
    port = int(os.getenv("CLICKHOUSE_HTTP_PORT", "8443" if secure else "8123"))
    if not 1 <= port <= 65535:
        raise ValueError("CLICKHOUSE_HTTP_PORT is outside the valid range.")

    return clickhouse_connect.get_client(
        host=host, port=port, username=user, password=password,
        database=database, secure=secure, verify=True,
        connect_timeout=10, send_receive_timeout=60,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=BASE / "schema.yaml")
    parser.add_argument("--manifest", type=Path, default=BASE / "data_manifest.yaml")
    parser.add_argument("--apply", action="store_true", help="Create tables.")
    args = parser.parse_args()

    schema_path, manifest_path = args.schema.resolve(), args.manifest.resolve()
    schema, manifest = read_yaml(schema_path), read_yaml(manifest_path)
    tables = validate_sources(schema, manifest, manifest_path)
    database = schema["database"]

    if not args.apply:
        print("\nDry run: no database connection or changes.")
        for spec in tables.values():
            print(create_statement(database, spec) + ";\n")
        return

    with connect(database) as client:
        # Preflight every existing table before creating any new table.
        for spec in tables.values():
            check_existing(client, database, spec)
        for spec in tables.values():
            client.command(create_statement(database, spec))
            if not check_existing(client, database, spec):
                raise RuntimeError(f"{spec['target']}: creation was not confirmed.")
            print(f"Ready: {database}.{spec['target']}")


if __name__ == "__main__":
    main()
