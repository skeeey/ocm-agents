## Prepare

1. Create a virtual environment

```sh
VENV=<your-python-virtual-environment-dir>
python -m venv $VENV
source $VENV/bin/activate
```

2. Install dependents

```sh
make deps
```

## Diagnosis Issue

```sh
VENV=<your-python-virtual-environment-dir>
source $VENV/bin/activate

export GROQ_API_KEY=<your-groq-api-key> # https://console.groq.com/docs/models
python -m apps.diagnosis --runbooks=<your-runbooks-dir> --hub-mg=<your-hub-must-gather-dir> --cluster-mg=<your-managed-cluster-must-gather-dir> <your-issue>
```

## Create Runbooks from Jira issue

```sh
VENV=<your-python-virtual-environment-dir>
source $VENV/bin/activate

export JIRA_SERVER=https://issues.redhat.com
export JIRA_TOKEN=<your-jira-token> # https://issues.redhat.com/secure/ViewProfile.jspa?selectedTab=com.atlassian.pats.pats-plugin:jira-user-personal-access-tokens
export GROQ_API_KEY=<your-groq-api-key> # https://console.groq.com/docs/models

python -m apps.runbook <your-jira-issue-id>
```
