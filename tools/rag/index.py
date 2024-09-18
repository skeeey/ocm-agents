# coding: utf-8

"""
Build the index with the given data and save the index to the local file system
"""

import logging
import time
import chromadb
from llama_index.core import StorageContext
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from .loaders import load_all_data
from .settings import LOG_FORMAT, LOG_DATE_FORMAT, INDEX_DIR

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if INDEX_DIR is None:
        raise ValueError("'INDEX_DIR' is required")

    # Set embedding model
    # https://huggingface.co/BAAI/bge-small-en-v1.5
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Load Data
    docs = load_all_data()
    if len(docs) == 0:
        raise ValueError("no documents are provided")

    db = chromadb.PersistentClient(path=INDEX_DIR)
    chroma_collection = db.get_or_create_collection("acm")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Build index
    logger.info("build index ...")
    start_time = time.time()
    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=StorageContext.from_defaults(vector_store=vector_store),
        # need more test, refer to
        # https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5
        # transformations=[SentenceSplitter(chunk_size=512, chunk_overlap=10)],
        show_progress=True,
    )
    logger.info("index is built, time used %.3fs", (time.time() - start_time))
