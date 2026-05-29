from dotenv import load_dotenv
import structlog
import hashlib
import redis
import time

load_dotenv()
log = structlog.get_logger()


def log_interaction(user_id: str, model: str, usage, latency_ms: int):
    """Log API call metadata without storing PII or prompt content."""
    log.info(
        "api_call",
        user_id_hash=hashlib.sha256(user_id.encode()).hexdigest()[:12],
        model=model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        latency_ms=latency_ms,
    )


def delete_user(user_id: str, db, vector_store, cache):
    """GDPR Art. 17 right to erasure — covers all storage layers."""
    db.delete_conversations(user_id)
    db.delete_profile(user_id)
    vector_store.delete(where={"user_id": user_id})
    cache.delete_pattern(f"session:{user_id}:*")
    log.info("user_deleted", user_id_hash=hashlib.sha256(user_id.encode()).hexdigest()[:12])


def check_rate_limit(user_id: str, limit: int = 20, window: int = 60) -> bool:
    """Token-bucket rate limiter backed by Redis."""
    try:
        r = redis.Redis(host="redis", decode_responses=True)
        key = f"rl:{user_id}:{int(time.time()) // window}"
        current = r.incr(key)
        if current == 1:
            r.expire(key, window * 2)
        return current <= limit
    except redis.ConnectionError:
        return True  # Fail open if Redis is unavailable


if __name__ == "__main__":
    print("GDPR utilities loaded.")
    print("log_interaction: hashes user_id, never logs prompt text.")
    print("delete_user: covers DB, vector store, and cache.")
    print("check_rate_limit: requires Redis. Falls back to allow on connection error.")
