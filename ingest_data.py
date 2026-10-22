from pathlib import Path

from app.retrieval.embeddings import (
    get_embedding
)

from app.retrieval.vector_store import (
    create_collection,
    insert_document,
    persist_collection
)

create_collection()

kb_path = Path(
    "data/knowledge_base.txt"
)

text = kb_path.read_text(
    encoding="utf-8"
)

documents = text.split(
    "------------------------------------------------"
)

counter = 0

for doc in documents:

    doc = doc.strip()

    if not doc:
        continue

    embedding = get_embedding(doc)

    insert_document(
        idx=counter,
        embedding=embedding,
        payload={
            "text": doc
        }
    )

    counter += 1

persist_collection()

print("Knowledge Base Ingested Successfully.")