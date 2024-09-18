# coding: utf-8

import autogen
import chromadb
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.chroma import ChromaVectorStore
from autogen.agentchat.contrib.llamaindex_conversable_agent import LLamaIndexConversableAgent
from .settings import INDEX_DIR, GROQ_API_KEY

def query_engine_chromadb():
    db = chromadb.PersistentClient(path=INDEX_DIR)
    chroma_collection = db.get_or_create_collection("acm")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    index = VectorStoreIndex.from_vector_store(vector_store)
    return index.as_query_engine()

def query_agent(query_engine):
    query_tool = QueryEngineTool.from_defaults(
        query_engine(),
        name="acm_query_engine",
        description="A RAG engine with the knowledge about the Red Hat Advanced Cluster Management for Kubernetes.",
    )
    return ReActAgent.from_tools([query_tool], verbose=True)

if __name__ == "__main__":
    Settings.llm = Groq(model="llama-3.1-70b-versatile", api_key=GROQ_API_KEY)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    llm_config = {
        "config_list": [
            {
                "model": "llama-3.1-70b-versatile",
                "api_key": GROQ_API_KEY,
                "api_type": "groq",
                "temperature": 0.0,
            }
        ]
    }

    assistant = LLamaIndexConversableAgent(
        "acm_specialist",
        llama_index_agent=query_agent(query_engine=query_engine_chromadb),
        system_message="You help users to answer their question about the Red Hat Advanced Cluster Management for Kubernetes.",
        description="This agents helps users get the knowledge of Red Hat Advanced Cluster Management for Kubernetes",
    )

    user_proxy = autogen.UserProxyAgent(
        name="Admin",
        human_input_mode="ALWAYS",
        code_execution_config=False,
    )

    groupchat = autogen.GroupChat(
        agents=[assistant, user_proxy],
        messages=[],
        max_round=500,
        speaker_selection_method="round_robin",
        enable_clear_history=True,
    )

    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    chat_result = user_proxy.initiate_chat(
        manager,
        message="Would you give me some instructions for troubleshooting Red Hat Advanced Cluster Management for Kubernetes imported clusters are offline after CA change?",
    )
