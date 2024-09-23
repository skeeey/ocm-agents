# coding: utf-8

import os
from jira import JIRA
# from unstructured.partition.md import optional_decode
from unstructured.partition.md import partition_md

def load_markdowns(dir, exclude_list=None):
    if exclude_list is None:
        exclude_list = ["README.md", "SECURITY.md", "GUIDELINE.md", "index.md"]

    files = _list_files(dir, exclude_list)
    docs = []
    for md in files:
        #  with open(md, encoding="utf8") as f:
        #     text = optional_decode(f.read())
        #     docs.append(text)
        # TODO: need test, this will output plain text
        elements = partition_md(filename=md)
        text = "\n\n".join([str(el) for el in elements])
        docs.append(text)

    all = "\n\n---\n\nRunbook: ".join(docs)
    return "Runbook: " + all

def load_jira(server_url, api_token, query):
    options = {
        "server": server_url,
        "headers": {"Authorization": f"Bearer {api_token}"},
    }
    
    jira = JIRA(options=options)

    return jira.search_issues(query)

def _list_files(start_path, exclude_list, suffix=".md"):
    file_list = []
    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if not d == '.git']
        
        for f in files:
            if f.endswith(suffix) and f not in exclude_list:
                file_list.append(os.path.join(root, f))

    return file_list

