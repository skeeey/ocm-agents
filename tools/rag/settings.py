# coding: utf-8

import os
from dotenv import load_dotenv

load_dotenv()

# log settings
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = "%(levelname)s: [%(asctime)s, %(module)s, line:%(lineno)d] %(message)s"

# model settings
LLM_MODEL = os.getenv("LLM_MODEL", default="llama3.1")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# index settings
INDEX_DIR = os.getenv("INDEX_DIR")

# local data settings
LOCAL_DATA_DIR = os.getenv("LOCAL_DATA_DIR")

# jira data settings
JIRA_SEVER = os.getenv("JIRA_SEVER")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
