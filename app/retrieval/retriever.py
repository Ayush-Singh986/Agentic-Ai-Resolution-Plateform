from app.retrieval.embeddings import (
    get_embedding
)

from app.retrieval.vector_store import (
    search_documents,
    create_collection
)

create_collection()


def retrieve_context(query: str):

    embedding = get_embedding(query)

    results = search_documents(
        embedding,
        limit=3
    )

    context = []

    for result in results:

        context.append(
            result.payload["text"]
        )

    return context