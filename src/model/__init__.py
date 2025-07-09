import hashlib

from sqlalchemy import (
    Column, String, Integer, Text, ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base, validates

Base = declarative_base()

# Association tables
issue_tag = Table(
    "issue_tag", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

issue_bug = Table(
    "issue_bug", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("bug_id", ForeignKey("bug.id"), primary_key=True),
)

issue_worklog = Table(
    "issue_worklog", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("worklog_id", ForeignKey("worklog.id"), primary_key=True),
)

issue_thanks = Table(
    "issue_thanks", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("thanks_id", ForeignKey("thanks.id"), primary_key=True),
)

issue_page = Table(
    "issue_page", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("page_hash", ForeignKey("page.hash"), primary_key=True),
)

issue_sysvar = Table(
    "issue_sysvar", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("sysvar_id", ForeignKey("sysvar.id"), primary_key=True),
)

issue_statvar = Table(
    "issue_statvar", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("statvar_id", ForeignKey("statvar.id"), primary_key=True),
)

issue_option = Table(
    "issue_option", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("option_id", ForeignKey("option.id"), primary_key=True),
)

issue_command = Table(
    "issue_command", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("command_id", ForeignKey("command.id"), primary_key=True),
)


class Release(Base):
    __tablename__ = "release"

    id = Column(Integer, primary_key=True)
    version = Column(String(20), nullable=False, unique=True)  # e.g. '5.7.33'
    release_date = Column(String(100), nullable=False)
    status = Column(String(100), nullable=False)

    issues = relationship("Issue", back_populates="release", cascade="all, delete-orphan")


class Issue(Base):
    __tablename__ = "issue"

    id = Column(Integer, primary_key=True)
    release_id = Column(Integer, ForeignKey("release.id"), nullable=False)
    text = Column(Text, nullable=False)

    release = relationship("Release", back_populates="issues")

    tags = relationship("Tag", secondary=issue_tag)
    bugs = relationship("Bug", secondary=issue_bug)
    worklogs = relationship("Worklog", secondary=issue_worklog)
    thanks = relationship("Thanks", secondary=issue_thanks)
    pages = relationship("Page", secondary=issue_page)
    sysvars = relationship("SysVar", secondary=issue_sysvar)
    statvars = relationship("StatVar", secondary=issue_statvar)
    options = relationship("Option", secondary=issue_option)
    commands = relationship("Command", secondary=issue_command)


# Lookup tables

class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    tag = Column(String(255), nullable=False, unique=True)


class Bug(Base):
    __tablename__ = "bug"
    id = Column(Integer, primary_key=True)
    bug = Column(String(20), nullable=False, unique=True)


class Worklog(Base):
    __tablename__ = "worklog"
    id = Column(Integer, primary_key=True)
    worklog = Column(String(20), nullable=False, unique=True)


class Thanks(Base):
    __tablename__ = "thanks"
    id = Column(Integer, primary_key=True)
    contributor = Column(String(255), nullable=False, unique=True)


class SysVar(Base):
    __tablename__ = "sysvar"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class StatVar(Base):
    __tablename__ = "statvar"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class Option(Base):
    __tablename__ = "option"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class Command(Base):
    __tablename__ = "command"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class Page(Base):
    __tablename__ = "page"

    hash = Column(String(64), primary_key=True)
    url = Column(String(2048), nullable=False)

    @validates("url")
    def generate_hash(self, key, value):
        if not value:
            raise ValueError("Page.url cannot be empty or null")
        self.hash = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return value
