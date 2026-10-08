import os
import time
import asyncio
import logging
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.llm import gpt_4o_mini_complete, openai_embedding
from lightrag.kg.postgres_impl import PostgreSQLDB
from dotenv import load_dotenv

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

WORKING_DIR = "./dickens"

# if not os.path.exists(WORKING_DIR):
#     os.mkdir(WORKING_DIR)

load_dotenv()

# Add PostgreSQL configuration
postgres_db = PostgreSQLDB(
    config={
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "lr"),
        "password": os.getenv("POSTGRES_PASSWORD", "local-light-rag-password"),
        "database": os.getenv("POSTGRES_DB", "lr_hello_world"),
    }
)

# Add AGE configuration
os.environ["AGE_POSTGRES_DB"] = os.getenv("POSTGRES_DB", "lr_hello_world")
os.environ["AGE_POSTGRES_USER"] = os.getenv("POSTGRES_USER", "lr")
os.environ["AGE_POSTGRES_PASSWORD"] = os.getenv("POSTGRES_PASSWORD", "local-light-rag-password")
os.environ["AGE_POSTGRES_HOST"] = os.getenv("POSTGRES_HOST", "localhost")
os.environ["AGE_POSTGRES_PORT"] = os.getenv("POSTGRES_PORT", "5432")
os.environ["AGE_GRAPH_NAME"] = "dickens"

async def main():
    # Initialize PostgreSQL
    await postgres_db.initdb()
    await postgres_db.check_tables()

    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        llm_model_max_async=4,
        llm_model_max_token_size=32768,
        enable_llm_cache_for_entity_extract=True,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            max_token_size=8192,
            func=openai_embedding
        ),
        # Add PostgreSQL storage configurations
        kv_storage="PGKVStorage",
        doc_status_storage="PGDocStatusStorage",
        graph_storage="AGEStorage",
        vector_storage="PGVectorStorage",
    )

    # Set PostgreSQL database connections
    rag.doc_status.db = postgres_db
    rag.full_docs.db = postgres_db
    rag.text_chunks.db = postgres_db
    rag.llm_response_cache.db = postgres_db
    rag.key_string_value_json_storage_cls.db = postgres_db
    rag.chunks_vdb.db = postgres_db
    rag.relationships_vdb.db = postgres_db
    rag.entities_vdb.db = postgres_db
    rag.graph_storage_cls.db = postgres_db
    rag.chunk_entity_relation_graph.db = postgres_db
    # Add embedding function for graph database
    rag.chunk_entity_relation_graph.embedding_func = rag.embedding_func

    book_path = "./book.txt"
    if not os.path.exists(book_path):
        raise FileNotFoundError(f"Book file not found at {book_path}")

    try:
        with open(book_path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                raise ValueError("Book file is empty")
            print(f"Read {len(content)} characters from {book_path}")
            
            print("Clearing existing database state...")
            await postgres_db.clear_all_tables()
            
            print("Inserting content into RAG...")
            await rag.ainsert(content)
            print("Content insertion complete")
    except Exception as e:
        print(f"Error processing book file: {e}")
        raise

    print("==== Testing RAG queries ====")
    query = "What are the top themes in this story?"

    print("**** Start Naive Query ****")
    start_time = time.time()
    print(await rag.aquery(query, param=QueryParam(mode="naive")))
    print(f"Naive Query Time: {time.time() - start_time} seconds")

    print("\n**** Start Local Query ****")
    start_time = time.time()
    print(await rag.aquery(query, param=QueryParam(mode="local")))
    print(f"Local Query Time: {time.time() - start_time} seconds")

    print("\n**** Start Global Query ****")
    start_time = time.time()
    print(await rag.aquery(query, param=QueryParam(mode="global")))
    print(f"Global Query Time: {time.time() - start_time} seconds")

    print("\n**** Start Hybrid Query ****")
    start_time = time.time()
    print(await rag.aquery(query, param=QueryParam(mode="hybrid")))
    print(f"Hybrid Query Time: {time.time() - start_time} seconds")

if __name__ == "__main__":
    asyncio.run(main())
