try:

    import redis

    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        decode_responses=True
    )

    redis_client.ping()

    REDIS_AVAILABLE = True

    print("Connected to Redis")

except Exception:

    REDIS_AVAILABLE = False

    print(
        "Redis unavailable. Using in-memory store."
    )

    memory_store = {}


def save_incident_memory(
        incident_id,
        response
):

    if REDIS_AVAILABLE:

        redis_client.set(
            incident_id,
            str(response)
        )

    else:

        memory_store[
            incident_id
        ] = response


def fetch_incident_memory(
        incident_id
):

    if REDIS_AVAILABLE:

        return redis_client.get(
            incident_id
        )

    return memory_store.get(
        incident_id
    )