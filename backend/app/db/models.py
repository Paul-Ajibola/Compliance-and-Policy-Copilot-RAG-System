import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Integer, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Placeholder embedding dimensions. Replace with actual if using
# different model. Using 1536 because that's typical for OpenAI models.
EMBEDDING_DIM = 1536


class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500))
    source_path: Mapped[str] = mapped_column(String(1000))

    department: Mapped[str | None] = mapped_column(String(200), nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    lifecycle_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    document_owner: Mapped[str | None] = mapped_column(String(200), nullable=True)
    review_cycle: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer)

    text: Mapped[str] = mapped_column(Text)
    chunk_type: Mapped[str] = mapped_column(String(20))  # "text" or "table"
    heading_path: Mapped[list] = mapped_column(JSON)

    # Nullable until Phase 3 backfills embeddings.
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["Document"] = relationship(back_populates="chunks")


    