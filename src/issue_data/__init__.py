import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup


@dataclass
class Issue:
    issuetext: str = field(repr=False)

    tags: list[str] | None = None
    bugs: list[str] | None = None
    worklogs: list[str] | None = None
    thanks: list[str] | None = None
    pages: list[str] | None = None
    sysvars: list[str] | None = None
    statvars: list[str] | None = None
    options: list[str] | None = None
    commands: list[str] | None = None


@dataclass
class Issues:
    rel_no: str
    rel_date: str
    rel_status: str

    issues: list[Issue]
    title: str | None = field(default=None, repr=False, init=False)
    soup: BeautifulSoup | None = field(default=None, repr=False, init=False)

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")
        self.issues = list()

        self.title = self.soup.find("title").get_text()
        self.parse_title()
        self.parse_sects()

    def parse_title(self) -> None:
        pattern = r"Changes in MySQL (?P<rel_no>\d+\.\d+\.\d+) \((?P<rel_date>[^,]+), (?P<rel_status>[^)]+)\)"
        match = re.search(pattern, self.title)
        if match:
            self.rel_no = match.group("rel_no")
            self.rel_date = match.group("rel_date")
            self.rel_status = match.group("rel_status")
        else:
            print("Could not parse title.")

    def parse_sects(self):
        # Section Title, if present
        for section in self.soup.find_all("div", class_="simplesect"):
            section_title = section.find("h3", class_="title")
            if section_title:
                section_title = section_title.get_text().strip()
            else:
                section_title = "No Section Title"

            # Issue List
            issue_list = section.find_all("li", class_="listitem")
            for issue in issue_list:
                tags = list()
                tags.append(section_title)

                full_text = issue.get_text(separator=" ", strip=True)
                bugs = re.findall(r"Bug\s+#(\d+)", full_text)
                worklogs = re.findall(r"WL\s+#(\d+)", full_text)
                thanks = re.findall(r"Our thanks to (.+) for the contribution", full_text)

                page_ref = list()
                option_ref = list()
                command_ref = list()
                sysvar_ref = list()
                statvar_ref = list()

                ulinks = issue.find_all("a", class_="ulink")
                for ulink in ulinks:
                    href = ulink.get("href")
                    if href:
                        if "sysvar" in href:
                            sysvar_ref = ulink.get_text().strip()
                        elif "statvar" in href:
                            statvar_ref = ulink.get_text().strip()
                        else:
                            page_ref.append(href)

                options = issue.find_all(class_="option")
                for option in options:
                    option_ref.append(option.get_text())

                commands = issue.find_all(class_="command")
                for command in commands:
                    command_ref.append(command.get_text())

                i = Issue(
                    issuetext=full_text,
                    tags=tags,
                    bugs=bugs,
                    worklogs=worklogs,
                    thanks=thanks,
                    pages=page_ref,
                    sysvars=sysvar_ref,
                    statvars=statvar_ref,
                    options=option_ref,
                    commands=command_ref
                )
                self.issues.append(i)
