import datetime as dt

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SessionRecord(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    questions: Mapped[list["QuestionRecord"]] = relationship(back_populates="session")


class QuestionRecord(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"))
    question: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String, default="")
    report: Mapped[str] = mapped_column(Text, default="")
    ranking: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    session: Mapped["SessionRecord"] = relationship(back_populates="questions")
    feedback: Mapped[list["FeedbackRecord"]] = relationship(back_populates="question")


class FeedbackRecord(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    rating: Mapped[str] = mapped_column(String)  # positivo | negativo | parcial | especialista
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    question: Mapped["QuestionRecord"] = relationship(back_populates="feedback")
