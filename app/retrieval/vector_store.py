import faiss
import numpy as np
import pickle
import os

INDEX_PATH = "data/faiss.index"
DOCS_PATH = "data/documents.pkl"

dimension = 384

index = faiss.IndexFlatL2(dimension)

documents = []


def create_collection():
    """
    Initialize collection.
    """

    global index
    global documents

    if os.path.exists(INDEX_PATH) and os.path.exists(DOCS_PATH):

        index = faiss.read_index(INDEX_PATH)

        with open(DOCS_PATH, "rb") as f:
            documents = pickle.load(f)

        print("Existing FAISS index loaded.")

    else:

        index = faiss.IndexFlatL2(dimension)
        documents = []

        print("New FAISS index created.")


def insert_document(
        idx: int,
        embedding,
        payload
):

    global index
    global documents

    vector = np.array(
        [embedding],
        dtype=np.float32
    )

    index.add(vector)

    documents.append(payload)


def persist_collection():

    global index

    faiss.write_index(
        index,
        INDEX_PATH
    )

    with open(DOCS_PATH, "wb") as f:
        pickle.dump(documents, f)

    print("FAISS index persisted.")


def search_documents(
        embedding,
        limit=3
):

    global index

    if index.ntotal == 0:
        return []

    query = np.array(
        [embedding],
        dtype=np.float32
    )

    distances, indices = index.search(
        query,
        limit
    )

    results = []

    for idx in indices[0]:

        if idx < len(documents):

            class SearchResult:
                pass

            result = SearchResult()

            result.payload = documents[idx]

            results.append(result)

    return results