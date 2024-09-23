# coding: utf-8

import click
import os
from dotenv import load_dotenv
from groq import Groq
from tools.loader import load_jira

load_dotenv()

@click.command()
@click.argument("issue")
def main(issue):
    server=os.getenv("JIRA_SERVER")
    token=os.getenv("JIRA_TOKEN")
    
    issues = load_jira(server_url=server, api_token=token, query=f"key={issue}")
    
    all_comments = ""
    for issue in issues:
        if issue.fields.comment.comments:
            comments = []
            for comment in issue.fields.comment.comments:
                comments.append(comment.body)
            all_comments = "\n".join(comments)
    
    text=f"{issue.fields.summary} \n {issue.fields.description} \n {all_comments}"

    llm = Groq(api_key=os.getenv("GROQ_API_KEY"))

    chat_completion = llm.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "you are a Red Hat Advanced Cluster Management for Kubernetes (ACM or RHACM) assistant."
            },
            {
                "role": "user",
                "content": f"""
The following content is about an ACM issue, please 
- Summarize the issue
- Give the issue's symptom
- Give the troubleshooting steps for this issue
- Give the solution of this issue

Here is the content

{text}

""",
            }
        ],
        model="llama-3.1-70b-versatile",
    )

    print(chat_completion.choices[0].message.content)

if __name__ == "__main__":
    main()