# coding: utf-8

# inspired by llama-index-readers-jira, we do some customization for our case
from typing import List, Optional, TypedDict
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document

from jira import JIRA

class BasicAuth(TypedDict):
    email: str
    api_token: str
    server_url: str


class Oauth2(TypedDict):
    cloud_id: str
    api_token: str


class PATauth(TypedDict):
    server_url: str
    api_token: str


class JiraReader(BaseReader):
    """Jira reader. Reads data from Jira issues from passed query.

    Args:
        Optional basic_auth:{
            "email": "email",
            "api_token": "token",
            "server_url": "server_url"
        }
        Optional oauth:{
            "cloud_id": "cloud_id",
            "api_token": "token"
        }
        Optional pat_auth:{
            "server_url": "server_url",
            "api_token": "token"
        }
    """

    def __init__(
        self,
        email: Optional[str] = None,
        api_token: Optional[str] = None,
        server_url: Optional[str] = None,
        basic_auth: Optional[BasicAuth] = None,
        oauth2: Optional[Oauth2] = None,
        pat_auth: Optional[PATauth] = None,
    ) -> None:
        if email and api_token and server_url:
            if basic_auth is None:
                basic_auth = {}
            basic_auth["email"] = email
            basic_auth["api_token"] = api_token
            basic_auth["server_url"] = server_url

        if oauth2:
            options = {
                "server": f"https://api.atlassian.com/ex/jira/{oauth2['cloud_id']}",
                "headers": {"Authorization": f"Bearer {oauth2['api_token']}"},
            }
            self.jira = JIRA(options=options)
        elif pat_auth:
            options = {
                "server": pat_auth["server_url"],
                "headers": {"Authorization": f"Bearer {pat_auth['api_token']}"},
            }
            self.jira = JIRA(options=options)
        else:
            self.jira = JIRA(
                basic_auth=(basic_auth["email"], basic_auth["api_token"]),
                server=f"https://{basic_auth['server_url']}",
            )

    def load_data(self, query: str) -> List[Document]:
        relevant_issues = self.jira.search_issues(query)

        issues = []

        for issue in relevant_issues:
            affects_versions = []
            fix_versions = []
            components = []
            all_comments = ""

            if issue.fields.versions:
                for version in issue.fields.versions:
                    affects_versions.append(version.name)

            if issue.raw["fields"]["fixVersions"]:
                for fix_version in issue.raw["fields"]["fixVersions"]:
                    fix_versions.append(fix_version["name"])

            if issue.raw["fields"]["components"]:
                for component in issue.raw["fields"]["components"]:
                    components.append(component["name"])

            if issue.fields.comment.comments:
                comments = []
                for comment in issue.fields.comment.comments:
                    comments.append(comment.body)
                all_comments = "\n".join(comments)

            issues.append(Document(
                    text=f"{issue.fields.summary} \n {issue.fields.description} \n {all_comments}",
                    extra_info={
                        "id": issue.key,
                        "labels": issue.fields.labels,
                        "components": components,
                        "status": issue.fields.status.name,
                        "assignee": issue.fields.assignee.emailAddress,
                        "reporter": issue.fields.reporter.emailAddress,
                        "project": issue.fields.project.name,
                        "issue_type": issue.fields.issuetype.name,
                        "affects_versions": affects_versions,
                        "fix_versions": fix_versions,
                    },
            ))

        return issues
