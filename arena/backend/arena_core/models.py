"""ORM models: a Submission and its (optional) Result."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base
from .ids import make_submission_id


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _gen_submission_id(context) -> str:
    # Context-sensitive default: derive the id from the row's handle at insert time,
    # so every Submission (API or a direct insert) gets a handle-based id.
    return make_submission_id(context.get_current_parameters()["handle"])


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(48), primary_key=True, default=_gen_submission_id)
    handle: Mapped[str] = mapped_column(String(64))
    mode: Mapped[str] = mapped_column(String(16), default="preset")    # preset | byoi (future)
    preset: Mapped[str] = mapped_column(String(32))
    files: Mapped[str] = mapped_column(Text)                            # JSON-encoded {relpath: content}
    build_cmd: Mapped[str | None] = mapped_column(Text, nullable=True)
    run_cmd: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="queued")   # queued|running|scored|failed
    fail_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow)

    result: Mapped["Result | None"] = relationship(
        back_populates="submission", uselist=False, cascade="all, delete-orphan"
    )


class Result(Base):
    __tablename__ = "results"

    submission_id: Mapped[str] = mapped_column(String(48), ForeignKey("submissions.id"), primary_key=True)
    length: Mapped[int] = mapped_column(Integer)
    runtime_ms: Mapped[int] = mapped_column(Integer)
    tour: Mapped[str] = mapped_column(Text)               # JSON-encoded list[int]
    gen_log: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON-encoded list (optional)

    submission: Mapped["Submission"] = relationship(back_populates="result")
