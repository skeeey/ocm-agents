# coding: utf-8

import os
import logging
import time
import autogen
import click
from autogen.coding import LocalCommandLineCodeExecutor
# from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
# from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor
from dotenv import load_dotenv
from tools.loader import load_markdowns
from prompts.templates import PLANNER_PROMPT, ANALYST_PROMPT

# log settings
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT = "%(levelname)s: [%(asctime)s, %(module)s, line:%(lineno)d] %(message)s"

load_dotenv()

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.realpath(__file__))
work_dir=os.path.join(current_dir, "__workspace__")

llm_config = {
    "config_list": [
        {
            "model": "llama-3.1-70b-versatile",
            "api_key": os.getenv("GROQ_API_KEY"),
            "api_type": "groq",
            "temperature": 0.0,
        }
    ]
}

def user_agent(human_input_mode):
    return autogen.UserProxyAgent(
        name="User",
        human_input_mode=human_input_mode,
        is_termination_msg=is_termination_message,
        code_execution_config=False,
    )

def planner_agent(llm_config, system_msg, human_input_mode):
    return autogen.AssistantAgent(
        name="Planner",
        description="Planner analyzes the User issues and creating diagnosis plan.",
        is_termination_msg=is_termination_message,
        human_input_mode=human_input_mode,
        llm_config=llm_config.copy(),
        system_message=system_msg,
    )

def analyst_agent(llm_config, system_msg, human_input_mode):
    return autogen.AssistantAgent(
        name="Analyst",
        description="Analyst analyzes the Planner's plan and converts the plan to executable command/scripts.",
        is_termination_msg=is_termination_message,
        human_input_mode=human_input_mode,
        llm_config=llm_config.copy(),
        system_message=system_msg,
    )

def executor_agent():
    return autogen.UserProxyAgent(
        name="Executor",
        description="Executor executes the code written by the Analyst and reports the result to Planner.",
        llm_config=False,
        code_execution_config={
            "executor": LocalCommandLineCodeExecutor(
                timeout=10,
                work_dir=work_dir,
            )
        },
        human_input_mode="NEVER",
    )

def selection(user, planner, analyst, executor, human_input_mode="NEVER"):
    def custom_speaker_selection_func(last_speaker, groupchat):
        content = groupchat.messages[-1]["content"]
        if "TERMINATE" in content:
                print(content)
                return None

        if last_speaker == user:
            return planner
        if last_speaker == planner:
            wait(human_input_mode=human_input_mode)
            return analyst
        if last_speaker == analyst:
            return executor
        if last_speaker == executor:
            wait(human_input_mode=human_input_mode)
            return planner
        
        return None
    return custom_speaker_selection_func

def is_termination_message(msg):
    return msg.get("content") is not None and (msg.get("content", "").rstrip().endswith("TERMINATE"))

def wait(human_input_mode, wait_time=5):
     if human_input_mode == "NEVER":
        time.sleep(wait_time)

@click.command()
@click.option("--runbooks", required=True, type=click.Path(file_okay=True, dir_okay=True, exists=True), help="the path of runbooks")
@click.option("--hub-mg", required=True, type=click.Path(file_okay=False, dir_okay=True, exists=True), help="the path of hub must-gather")
@click.option("--cluster-mg", type=click.Path(file_okay=False, dir_okay=True, exists=True), help="the path of managed cluster must-gather")
@click.option("--enable-human-input", is_flag=True, default=False, help="enable human input mode")
@click.argument("issue")
def main(runbooks, hub_mg, cluster_mg, enable_human_input, issue):
    human_input_mode="NEVER"

    if cluster_mg is None:
        cluster_mg = hub_mg

    if enable_human_input is True:
        human_input_mode="ALWAYS"
    
    logger.debug("runbooks=%s,hub-must-gather=%s,managed-cluster-must-gather=%s", runbooks, hub_mg, cluster_mg)

    runbook_contents = load_markdowns(runbooks)

    # llm_lingua = LLMLingua()
    # text_compressor = TextMessageCompressor(text_compressor=llm_lingua)
    # compressed_contents = text_compressor.apply_transform([{"content": runbook_contents}])
    # logger.debug(compressed_contents)

    planner_prompt = PLANNER_PROMPT.format(context=runbook_contents)
    analyst_prompt = ANALYST_PROMPT.format(hub_dir=hub_mg, spoke_dir=cluster_mg)
    
    logger.debug(llm_config)
    logger.debug(planner_prompt)

    user = user_agent(human_input_mode)
    planner = planner_agent(llm_config, planner_prompt, human_input_mode)
    analyst = analyst_agent(llm_config, analyst_prompt, human_input_mode)
    executor = executor_agent()

    user.reset()
    planner.reset()
    analyst.reset()

    group_chat = autogen.GroupChat(
        agents=[user, planner, analyst, executor],
        max_round=50,
        messages=[],
        speaker_selection_method=selection(user, planner, analyst, executor, human_input_mode),
        send_introductions=True,
    )
    user.initiate_chat(
        autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config, silent=False),
        message=issue,
    )

if __name__ == "__main__":
    main()
