import os
import re
from collections.abc import Iterable
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from typing import Any

from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, MetaData, String, Table, Text, create_engine, delete, func, insert, select, update, JSON
from sqlalchemy.exc import SQLAlchemyError

JSONB = JSON



try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql+psycopg2://"):
        return url
    if url.startswith("postgresql://"):
        return "postgresql+psycopg2://" + url[len("postgresql://"):]
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://"):]
    return url


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL")
    or os.getenv("SUPABASE_DATABASE_URL")
    or "sqlite:///local.db"
)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, future=True)
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
metadata = MetaData()


def generate_id() -> str:
    return str(ObjectId())


users_table = Table(
    "users",
    metadata,
    Column("id", String(24), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("username", String(255), nullable=False, unique=True, index=True),
    Column("email", String(255), nullable=False, unique=True, index=True),
    Column("hashed_password", Text, nullable=False),
    Column("avatar", Text, nullable=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

workouts_table = Table(
    "workouts",
    metadata,
    Column("id", String(24), primary_key=True),
    Column("user_id", String(255), nullable=False, index=True),
    Column("type", String(255), nullable=False),
    Column("reps", Integer, nullable=False, default=0),
    Column("feedback", Text, nullable=False, default=""),
    Column("accuracy", Float, nullable=False, default=0.0),
    Column("timestamp", DateTime, nullable=False, default=datetime.utcnow, index=True),
)

friend_requests_table = Table(
    "friend_requests",
    metadata,
    Column("id", String(24), primary_key=True),
    Column("from_username", String(255), nullable=False, index=True),
    Column("to_username", String(255), nullable=False, index=True),
    Column("status", String(32), nullable=False, default="pending", index=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
    Column("responded_at", DateTime, nullable=True),
)

friends_table = Table(
    "friends",
    metadata,
    Column("id", String(24), primary_key=True),
    Column("user1", String(255), nullable=True, index=True),
    Column("user2", String(255), nullable=True, index=True),
    Column("user_id", String(255), nullable=True, index=True),
    Column("friend_id", String(255), nullable=True, index=True),
    Column("status", String(32), nullable=False, default="accepted", index=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

notifications_table = Table(
    "notifications",
    metadata,
    Column("id", String(24), primary_key=True),
    Column("user_id", String(255), nullable=False, index=True),
    Column("type", String(255), nullable=False),
    Column("title", Text, nullable=False),
    Column("message", Text, nullable=False),
    Column("data", JSONB, nullable=True),
    Column("read", Boolean, nullable=False, default=False, index=True),
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow, index=True),
)

user_points_table = Table(
    "user_points",
    metadata,
    Column("id", String(24), primary_key=True),
    Column("user_id", String(255), nullable=False, unique=True, index=True),
    Column("total_points", Integer, nullable=False, default=0),
    Column("exercise_points", JSONB, nullable=False, default=dict),
    Column("last_updated", DateTime, nullable=False, default=datetime.utcnow),
)

points_history_table = Table(
    "points_history",
    metadata,
    Column("id", String(24), primary_key=True),
    Column("user_id", String(255), nullable=False, index=True),
    Column("exercise", String(255), nullable=False, index=True),
    Column("reps_completed", Integer, nullable=False),
    Column("cycles_completed", Integer, nullable=False),
    Column("points_earned", Integer, nullable=False),
    Column("timestamp", DateTime, nullable=False, default=datetime.utcnow, index=True),
)

sessions_table = Table(
    "sessions",
    metadata,
    Column("id", String(24), primary_key=True),
    Column("user_id", String(255), nullable=False, index=True),
    Column("timestamp", DateTime, nullable=False, default=datetime.utcnow, index=True),
    Column("feedback", Text, nullable=False),
    Column("keypoints", JSONB, nullable=True),
)

TABLES = {
    "users": users_table,
    "workouts": workouts_table,
    "friend_requests": friend_requests_table,
    "friends": friends_table,
    "notifications": notifications_table,
    "user_points": user_points_table,
    "points_history": points_history_table,
    "sessions": sessions_table,
}

_tables_ready = False


def ensure_tables() -> None:
    global _tables_ready
    if _tables_ready:
        return
    try:
        metadata.create_all(engine)
        _tables_ready = True
    except SQLAlchemyError as exc:
        raise PyMongoError(str(exc)) from exc


@contextmanager
def get_connection():
    ensure_tables()
    with engine.begin() as connection:
        yield connection


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    return value


def _get_nested_value(document: dict[str, Any], dotted_key: str) -> Any:
    current: Any = document
    for part in dotted_key.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _set_nested_value(document: dict[str, Any], dotted_key: str, value: Any) -> None:
    parts = dotted_key.split(".")
    current = document
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            child = {}
            current[part] = child
        current = child
    current[parts[-1]] = value


def _document_matches(document: dict[str, Any], criteria: dict[str, Any] | None) -> bool:
    if not criteria:
        return True

    for key, expected in criteria.items():
        if key == "$or":
            return any(_document_matches(document, clause) for clause in expected)
        if key == "$and":
            return all(_document_matches(document, clause) for clause in expected)

        doc_value = _get_nested_value(document, key)

        if isinstance(expected, dict):
            for operator, operand in expected.items():
                if operator == "$options":
                    continue
                if operator == "$regex":
                    flags = re.IGNORECASE if str(expected.get("$options", "")).lower().find("i") != -1 else 0
                    if doc_value is None or re.search(str(operand), str(doc_value), flags) is None:
                        return False
                elif operator == "$gte":
                    if doc_value is None or doc_value < operand:
                        return False
                elif operator == "$in":
                    normalized_doc = _normalize_scalar(doc_value)
                    normalized_choices = {_normalize_scalar(item) for item in operand}
                    if normalized_doc not in normalized_choices:
                        return False
                else:
                    if _normalize_scalar(doc_value) != _normalize_scalar(operand):
                        return False
            continue

        if _normalize_scalar(doc_value) != _normalize_scalar(expected):
            return False

    return True


class InsertOneResult:
    def __init__(self, inserted_id: str):
        self.inserted_id = inserted_id


class UpdateOneResult:
    def __init__(self, modified_count: int):
        self.modified_count = modified_count


class DeleteOneResult:
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class QueryCursor:
    def __init__(self, documents: list[dict[str, Any]]):
        self._documents = documents

    def sort(self, field: str, direction: int):
        reverse = direction == -1
        self._documents.sort(key=lambda item: (item.get(field) is None, item.get(field)), reverse=reverse)
        return self

    def limit(self, limit_value: int):
        self._documents = self._documents[:limit_value]
        return self

    def __iter__(self):
        return iter(deepcopy(self._documents))

    def __len__(self):
        return len(self._documents)


class CollectionWrapper:
    def __init__(self, table: Table):
        self.table = table

    def _load_documents(self) -> list[dict[str, Any]]:
        with get_connection() as connection:
            rows = connection.execute(select(self.table)).mappings().all()
        documents: list[dict[str, Any]] = []
        for row in rows:
            document = dict(row)
            if "_id" not in document and "id" in document:
                document["_id"] = document["id"]
            elif "id" not in document and "_id" in document:
                document["id"] = document["_id"]
            documents.append(document)
        return documents

    def _filter_documents(self, filter_query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        documents = self._load_documents()
        return [document for document in documents if _document_matches(document, filter_query)]

    def find_one(self, filter_query: dict[str, Any] | None = None):
        matches = self._filter_documents(filter_query)
        return deepcopy(matches[0]) if matches else None

    def find(self, filter_query: dict[str, Any] | None = None):
        return QueryCursor(self._filter_documents(filter_query))

    def insert_one(self, document: dict[str, Any]):
        payload = deepcopy(document)
        document_id = str(payload.get("_id") or payload.get("id") or generate_id())
        payload["id"] = document_id
        payload.pop("_id", None)

        row = {}
        for column in self.table.columns:
            if column.name == "id":
                row[column.name] = payload["id"]
            else:
                row[column.name] = payload.get(column.name)

        try:
            with get_connection() as connection:
                connection.execute(insert(self.table).values(**row))
        except SQLAlchemyError as exc:
            raise PyMongoError(str(exc)) from exc

        return InsertOneResult(document_id)

    def update_one(self, filter_query: dict[str, Any], update_payload: dict[str, Any]):
        matches = self._filter_documents(filter_query)
        if not matches:
            return UpdateOneResult(0)

        original = matches[0]
        updated = deepcopy(original)

        set_payload = update_payload.get("$set", update_payload)
        for key, value in set_payload.items():
            if "." in key:
                root_key, nested_path = key.split(".", 1)
                container = updated.get(root_key)
                if not isinstance(container, dict):
                    container = {}
                _set_nested_value(container, nested_path, value)
                updated[root_key] = container
            else:
                updated[key] = value

        row_update = {
            column.name: updated.get(column.name)
            for column in self.table.columns
            if column.name != "id"
        }

        try:
            with get_connection() as connection:
                connection.execute(
                    update(self.table)
                    .where(self.table.c.id == original["id"])
                    .values(**row_update)
                )
        except SQLAlchemyError as exc:
            raise PyMongoError(str(exc)) from exc

        return UpdateOneResult(1)

    def delete_one(self, filter_query: dict[str, Any]):
        matches = self._filter_documents(filter_query)
        if not matches:
            return DeleteOneResult(0)

        original = matches[0]
        try:
            with get_connection() as connection:
                connection.execute(delete(self.table).where(self.table.c.id == original["id"]))
        except SQLAlchemyError as exc:
            raise PyMongoError(str(exc)) from exc

        return DeleteOneResult(1)

    def count_documents(self, filter_query: dict[str, Any]):
        return len(self._filter_documents(filter_query))

    def aggregate(self, pipeline: list[dict[str, Any]]):
        documents = self._load_documents()

        for stage in pipeline:
            if "$match" in stage:
                documents = [document for document in documents if _document_matches(document, stage["$match"])]
            elif "$group" in stage:
                group_spec = stage["$group"]
                grouped: dict[Any, dict[str, Any]] = {}

                for document in documents:
                    group_key = group_spec.get("_id")
                    if isinstance(group_key, str) and group_key.startswith("$"):
                        group_key = _get_nested_value(document, group_key[1:])

                    bucket = grouped.setdefault(group_key, {"_id": group_key, "__avg": {}})

                    for field_name, expression in group_spec.items():
                        if field_name == "_id":
                            continue
                        if isinstance(expression, dict) and "$sum" in expression:
                            operand = expression["$sum"]
                            if operand == 1:
                                value = 1
                            elif isinstance(operand, str) and operand.startswith("$"):
                                value = _get_nested_value(document, operand[1:]) or 0
                            else:
                                value = operand or 0
                            bucket[field_name] = bucket.get(field_name, 0) + value
                        elif isinstance(expression, dict) and "$avg" in expression:
                            operand = expression["$avg"]
                            if isinstance(operand, str) and operand.startswith("$"):
                                value = _get_nested_value(document, operand[1:]) or 0
                            else:
                                value = operand or 0
                            avg_bucket = bucket["__avg"].setdefault(field_name, {"sum": 0, "count": 0})
                            avg_bucket["sum"] += value
                            avg_bucket["count"] += 1

                aggregated: list[dict[str, Any]] = []
                for bucket in grouped.values():
                    for field_name, value in bucket.pop("__avg", {}).items():
                        bucket[field_name] = (value["sum"] / value["count"]) if value["count"] else 0
                    aggregated.append(bucket)
                documents = aggregated
            elif "$sort" in stage:
                sort_spec = stage["$sort"]
                for field_name, direction in reversed(list(sort_spec.items())):
                    reverse = direction == -1
                    documents.sort(key=lambda item: (item.get(field_name) is None, item.get(field_name)), reverse=reverse)
            elif "$limit" in stage:
                documents = documents[: stage["$limit"]]

        return QueryCursor(documents)


class DatabaseWrapper:
    def __getitem__(self, collection_name: str):
        table = TABLES.get(collection_name)
        if table is None:
            raise KeyError(collection_name)
        return CollectionWrapper(table)


db = DatabaseWrapper()


def get_database():
    return db


def get_user_collection():
    return db["users"]


def get_workout_collection():
    return db["workouts"]


def get_scores_collection():
    return db["user_points"]
