from datetime import datetime, timezone

from sqlalchemy import Column, DateTime


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_datetime_column(
    *,
    nullable: bool = False,
    onupdate: bool = False,
) -> Column:
    return Column(
        DateTime(timezone=True),
        nullable=nullable,
        onupdate=utc_now if onupdate else None,
    )
