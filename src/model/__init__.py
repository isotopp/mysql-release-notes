from sqlalchemy import (
    Column, String, Integer, Text, ForeignKey, Table
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Association tables for many-to-many fields
issue_tag = Table(
    "issue_tag", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("tag", ForeignKey("tag.tag"), primary_key=True),
)

issue_bug = Table(
    "issue_bug", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("bug", ForeignKey("bug.bug"), primary_key=True),
)

issue_worklog = Table(
    "issue_worklog", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("worklog", ForeignKey("worklog.worklog"), primary_key=True),
)

issue_thanks = Table(
    "issue_thanks", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("contributor", ForeignKey("thanks.contributor"), primary_key=True),
)

issue_page = Table(
    "issue_page", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("hash", ForeignKey("page.hash"), primary_key=True),
)

issue_sysvar = Table(
    "issue_sysvar", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("name", ForeignKey("sysvar.name"), primary_key=True),
)

issue_statvar = Table(
    "issue_statvar", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("name", ForeignKey("statvar.name"), primary_key=True),
)

issue_option = Table(
    "issue_option", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("name", ForeignKey("option.name"), primary_key=True),
)

issue_command = Table(
    "issue_command", Base.metadata,
    Column("issue_id", ForeignKey("issue.id"), primary_key=True),
    Column("name", ForeignKey("command.name"), primary_key=True),
)


class Release(Base):
    __tablename__ = "release"

    id = Column(Integer, primary_key=True)
    version = Column(String(20), nullable=False, unique=True)  # e.g. '5.7.33'
    release_date = Column(String(100), nullable=False)  # string for flexibility, e.g. 'Not released'
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


# Define simple wrapper tables for single attributes (for foreign key safety & reuse)
class Tag(Base):
    __tablename__ = "tag"
    tag = Column(String(255), primary_key=True)


class Bug(Base):
    __tablename__ = "bug"
    bug = Column(String(20), primary_key=True)


class Worklog(Base):
    __tablename__ = "worklog"
    worklog = Column(String(20), primary_key=True)


class Thanks(Base):
    __tablename__ = "thanks"
    contributor = Column(String(255), primary_key=True)


class Page(Base):
    __tablename__ = "page"

    hash = Column(String(64), primary_key=True)
    _url = Column("url", String(2048), nullable=False)

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        self._url = value
        self.hash = hashlib.sha256(value.encode("utf-8")).hexdigest()


class SysVar(Base):
    __tablename__ = "sysvar"
    name = Column(String(255), primary_key=True)


class StatVar(Base):
    __tablename__ = "statvar"
    name = Column(String(255), primary_key=True)


class Option(Base):
    __tablename__ = "option"
    name = Column(String(255), primary_key=True)


class Command(Base):
    __tablename__ = "command"
    name = Column(String(255), primary_key=True)
