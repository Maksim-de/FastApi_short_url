from sqlalchemy import (
    Table,
    Column,
    Integer,
    DateTime,
    MetaData,
    String,
    Boolean,
    Date,
    func,
    UniqueConstraint,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

metadata = MetaData()

links = Table(
    "links",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("login_user", String, nullable=True),
    Column("full_link", String),
    Column("short_link", String, unique=True),
    Column("number_of_click", Integer, default=0),  # Количество кликов по ссылке
    Column("creation_date", DateTime, default=datetime.now()),
    Column("date_use", DateTime, nullable=True),
    Column("expiration_date", DateTime, nullable=True),
    Column("is_deleted", Boolean, default=False),
)


User = Table(
    "user",
    metadata,
    Column("id", UUID, primary_key=True, index=True),
    Column("email", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=True, nullable=False),
    Column("is_verified", Boolean, default=True, nullable=False),
)
