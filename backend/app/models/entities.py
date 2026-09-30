from datetime import datetime, timezone
from typing import Optional, List, Any
from sqlalchemy import (
    Column, Integer, String, BigInteger, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Relationships
    profile: Mapped[Optional["Profile"]] = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    quizzes: Mapped[List["Quiz"]] = relationship("Quiz", back_populates="owner")
    attempts: Mapped[List["QuizAttempt"]] = relationship("QuizAttempt", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("files.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    avatar: Mapped[Optional["FileModel"]] = relationship("FileModel", foreign_keys=[avatar_id])


class FileModel(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    storage_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    media_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "video" | "image" | "audio" | null
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    thumbnail_parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Self-referential relationship for thumbnail parent/children
    thumbnails: Mapped[List["FileModel"]] = relationship(
        "FileModel",
        back_populates="parent_file",
        cascade="all, delete-orphan",
        foreign_keys=[thumbnail_parent_id]
    )
    parent_file: Mapped[Optional["FileModel"]] = relationship(
        "FileModel",
        back_populates="thumbnails",
        remote_side=[id],
        foreign_keys=[thumbnail_parent_id]
    )


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="private", nullable=False)  # "private" | "public"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="quizzes")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="quiz", cascade="all, delete-orphan", order_by="Question.order")
    attempts: Mapped[List["QuizAttempt"]] = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # "single" | "multiple" | "matching"

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
    options: Mapped[List["Option"]] = relationship("Option", back_populates="question", cascade="all, delete-orphan", order_by="Option.order")
    pairs: Mapped[List["QuestionPair"]] = relationship("QuestionPair", back_populates="question", cascade="all, delete-orphan", order_by="QuestionPair.order")
    answers: Mapped[List["AttemptAnswer"]] = relationship("AttemptAnswer", back_populates="question", cascade="all, delete-orphan")


class Option(Base):
    __tablename__ = "options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    question: Mapped["Question"] = relationship("Question", back_populates="options")


class QuestionPair(Base):
    __tablename__ = "question_pairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    left_text: Mapped[str] = mapped_column(Text, nullable=False)
    right_text: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    question: Mapped["Question"] = relationship("Question", back_populates="pairs")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts")
    user: Mapped["User"] = relationship("User", back_populates="attempts")
    answers: Mapped[List["AttemptAnswer"]] = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("options.id", ondelete="SET NULL"), nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    matching_pairs: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Relationships
    attempt: Mapped["QuizAttempt"] = relationship("QuizAttempt", back_populates="answers")
    question: Mapped["Question"] = relationship("Question", back_populates="answers")
    option: Mapped[Optional["Option"]] = relationship("Option")
