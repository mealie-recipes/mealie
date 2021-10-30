import json

import requests
from pydantic import BaseModel


class GithubIssue(BaseModel):
    url: str
    number: int
    title: str


def get_issues_by_label(label="fixed-pending-release") -> list[GithubIssue]:

    issues_url = f"https://api.github.com/repos/hay-kot/mealie/issues?labels={label}"

    response = requests.get(issues_url)
    issues = json.loads(response.text)
    return [GithubIssue(**issue) for issue in issues]


def format_markdown_list(issues: list[GithubIssue]) -> str:
    return "\n".join(f"- [{issue.number}]({issue.url}) - {issue.title}" for issue in issues)


def main() -> None:
    issues = get_issues_by_label()
    print(format_markdown_list(issues))


if __name__ == "__main__":
    main()
