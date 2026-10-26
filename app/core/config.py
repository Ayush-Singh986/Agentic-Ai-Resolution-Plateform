from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    MODEL_NAME: str = os.getenv(
        "MODEL_NAME",
        "llama-3.3-70b-versatile"
    )

    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092"
    )

    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    ECS_CLUSTER_NAME: str | None = os.getenv("ECS_CLUSTER_NAME")
    ECS_SERVICE_NAME: str | None = os.getenv("ECS_SERVICE_NAME")
    REMEDIATION_TABLE_NAME: str | None = os.getenv(
        "REMEDIATION_TABLE_NAME"
    )
    COGNITO_USER_POOL_ID: str | None = os.getenv(
        "COGNITO_USER_POOL_ID"
    )
    COGNITO_APP_CLIENT_ID: str | None = os.getenv(
        "COGNITO_APP_CLIENT_ID"
    )
    COGNITO_ISSUER_URL: str | None = os.getenv("COGNITO_ISSUER_URL")
    COGNITO_HOSTED_UI_DOMAIN: str | None = os.getenv(
        "COGNITO_HOSTED_UI_DOMAIN"
    )
    APP_PUBLIC_URL: str | None = os.getenv("APP_PUBLIC_URL")
    COGNITO_APPROVER_GROUP: str = os.getenv(
        "COGNITO_APPROVER_GROUP",
        "IncidentApprovers",
    )

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()