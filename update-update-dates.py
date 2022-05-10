"""
Script to update the "Last known update" column in the structural editors table.

It uses the GitHub CLI (requirement).
"""

import datetime
import json
import subprocess
import sys


github_repo_prefix = "https://github.com/"


def get_github_repo(markdown_hyperlink):
    assert markdown_hyperlink.startswith(
        "[") and markdown_hyperlink.endswith(")")
    content, link = markdown_hyperlink[1:-1].split("](", 1)
    if not link.startswith(github_repo_prefix):
        return markdown_hyperlink, None
    return content, link[len(github_repo_prefix):]


cur_year = datetime.datetime.today().year


def new_line(line):
    repo = None
    yearlink = None

    parts = line.split("|")
    name = parts[1].strip()
    prev_year = parts[-1].strip()
    if name.endswith(")"):
        _, repo = get_github_repo(name)
    if repo is None and prev_year.endswith(")"):
        prev_year, repo = get_github_repo(prev_year)
        yearlink = github_repo_prefix + repo
    if repo is None:
        return

    assert int(prev_year) <= cur_year
    if int(prev_year) == cur_year:
        # Current, no need to check if updated
        return

    key = "pushedAt"
    result = subprocess.check_output(
        ["gh", "repo", "view", repo, "--json", key])
    date = json.loads(result.decode("UTF-8"))[key]
    year = int(date.split("-", 1)[0])
    if yearlink is not None:
        year = f"[{year}]({yearlink})"
    head = line.rsplit("| ", 1)[0]
    return f"{head}| {year}\n"


def new_lines():
    lines = iter(open("README.md"))
    for line in lines:
        yield line
        if line.endswith(" | Last known update\n"):
            break
    else:
        print("Did not find table")
        sys.exit(1)
    yield next(lines)
    for line in lines:
        if not line.strip():
            yield line
            break
        yield new_line(line) or line
    yield from lines


res = "".join(new_lines())
open("README.md", "w").write(res)
