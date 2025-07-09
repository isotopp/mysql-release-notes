from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from caching_fetcher import *
from issue_data import Issues
from model import Base, Release, Issue, Tag, Bug, Worklog, Thanks, Page, SysVar, StatVar, Option, Command


def main() -> None:
    # Connect to the MySQL database
    engine = create_engine("mysql+mysqldb://kris:geheim@192.168.1.10/mysql_releases")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    five_seven = RELEASE_NOTES["5.7"]
    five_seven.fetch_release_notes()

    for release in five_seven.releases:
        parsed = Issues(release.releasenotes)
        print(f"{parsed.rel_no}: {len(parsed.issues)} issues")

        db_release = Release(
            version=parsed.rel_no,
            release_date=parsed.rel_date,
            status=parsed.rel_status
        )

        for parsed_issue in parsed.issues:
            issue = Issue(text=parsed_issue.issuetext)

            def attach(cls, items, rel):
                if not items:
                    return
                if isinstance(items, str):
                    items = [items]
                for val in set(items):
                    pk_col = list(cls.__table__.primary_key.columns)[0].name
                    obj = cls(**{pk_col: val})
                    obj = session.merge(obj)  # safely merge or insert
                    rel.append(obj)

            attach(Tag, parsed_issue.tags, issue.tags)
            attach(Bug, parsed_issue.bugs, issue.bugs)
            attach(Worklog, parsed_issue.worklogs, issue.worklogs)
            attach(Thanks, parsed_issue.thanks, issue.thanks)
            attach(Page, parsed_issue.pages, issue.pages)
            attach(SysVar, parsed_issue.sysvars, issue.sysvars)
            attach(StatVar, parsed_issue.statvars, issue.statvars)
            attach(Option, parsed_issue.options, issue.options)
            attach(Command, parsed_issue.commands, issue.commands)

            db_release.issues.append(issue)

        session.add(db_release)
        try:
            session.commit()
            print(f"Committed release {db_release.version}")
        except Exception as e:
            session.rollback()
            print(f"Error committing release {db_release.version}: {e}")
