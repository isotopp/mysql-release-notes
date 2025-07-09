from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

import requests

__all__ = ["Release", "ReleaseNotes", "RELEASE_NOTES"]

@dataclass(kw_only=True)
class Release:
    major: str
    minor: int
    releasenotes: str

    def __repr__(self) -> str:
        return f"Release(major='{self.major}', minor={self.minor}, releasenotes=<{len(self.releasenotes)} chars>)"


@dataclass(kw_only=True)
class ReleaseNotes:
    """ Tracking MySQL Releasenotes: a base url for each major release and a range of minor release numbers. """
    start: int
    end: int
    major: str
    base: str
    releases: list[Release] = field(default_factory=list)

    OUTPUT_DIR: ClassVar[Path] = Path("release_notes")

    def fetch_release_notes(self) -> None:
        for releaseno in range(self.start, self.end + 1):
            # Store the data here
            filename = Path(self.OUTPUT_DIR) / f"mysql-{self.major}.{releaseno}.html"

            # If we have the data, read it from a file
            if filename.exists():
                # print(f"Fetching from cache: {filename}")
                with open(filename, "r") as f:
                    rl = Release(major=self.major, minor=releaseno, releasenotes=f.read())
                    self.releases.append(rl)
                continue

            # Load the data from the web
            url = self.base.format(releaseno=releaseno)
            # print(f"Fetching: {url}")
            try:
                response = requests.get(url)
                response.raise_for_status()
                releasenotes = response.text
            except requests.HTTPError as e:
                print(f"Failed to fetch {url}: {e}")
                releasenotes = "Skipped Release"

            rl = Release(major=self.major, minor=releaseno, releasenotes=releasenotes)
            self.releases.append(rl)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(releasenotes)
                # print(f"Saved to: {filename}")

        return


RELEASE_NOTES = {
    "5.7": ReleaseNotes(start=0, end=44, major="5.7",
                        base="https://dev.mysql.com/doc/relnotes/mysql/5.7/en/news-5-7-{releaseno}.html"),
    "8.0": ReleaseNotes(start=0, end=43, major="8.0",
                        base="https://dev.mysql.com/doc/relnotes/mysql/8.0/en/news-8-0-{releaseno}.html"),
    "8.1": ReleaseNotes(start=0, end=0, major="8.1",
                        base="https://dev.mysql.com/doc/relnotes/mysql/8.1/en/news-8-1-{releaseno}.html"),
    "8.2": ReleaseNotes(start=0, end=0, major="8.2",
                        base="https://dev.mysql.com/doc/relnotes/mysql/8.2/en/news-8-2-{releaseno}.html"),
    "8.3": ReleaseNotes(start=0, end=0, major="8.3",
                        base="https://dev.mysql.com/doc/relnotes/mysql/8.3/en/news-8-3-{releaseno}.html"),
    "8.4": ReleaseNotes(start=0, end=5, major="8.4",
                        base="https://dev.mysql.com/doc/relnotes/mysql/8.4/en/news-8-4-{releaseno}.html"),
    "9.0": ReleaseNotes(start=0, end=1, major="9.0",
                        base="https://dev.mysql.com/doc/relnotes/mysql/9.0/en/news-9-0-{releaseno}.html"),
    "9.1": ReleaseNotes(start=0, end=0, major="9.1",
                        base="https://dev.mysql.com/doc/relnotes/mysql/9.1/en/news-9-1-{releaseno}.html"),
    "9.2": ReleaseNotes(start=0, end=0, major="9.2",
                        base="https://dev.mysql.com/doc/relnotes/mysql/9.2/en/news-9-2-{releaseno}.html"),
    "9.3": ReleaseNotes(start=0, end=0, major="9.3",
                        base="https://dev.mysql.com/doc/relnotes/mysql/9.3/en/news-9-3-{releaseno}.html"),
}
