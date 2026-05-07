from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC

from app.database import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    sequence_type: Mapped[str] = mapped_column(String(10))
    strand_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    input_sequence: Mapped[str] = mapped_column(Text)
    mrna_sequence: Mapped[str] = mapped_column(Text)
    protein_sequence: Mapped[str] = mapped_column(Text)
    summary_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
