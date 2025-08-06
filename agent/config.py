import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Config:
    # --- API Keys and Tokens ---
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    # New API Keys
    GEMINI_KEY_1 = os.getenv("GEMINI_KEY_1", "AIzaSyApjpQaZCJIjuBwWm7IeIVDRXle6u46t4I")
    GEMINI_KEY_2 = os.getenv("GEMINI_KEY_2", "AIzaSyCObpb_dJXNltBBRgMnvNLeYB9cfDcr710")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-cf7db1473cd049ffb4f0a4c758869495")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
    LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://127.0.0.1:40000")
    LOCAL_API_ID = os.getenv("LOCAL_API_ID", "1647909984704093")
    LOCAL_API_KEY = os.getenv("LOCAL_API_KEY", "8ae71f08f1a445778ae43bd8e406ad1b")

    # OpenRouter Free Models
    OPENROUTER_FREE_MODELS = [
        "meta-llama/llama-4-maverick:free",
        "meta-llama/llama-4-scout:free",
        "venice/uncensored:free",
        "cognitivecomputations/dolphin-mixtral-8x22b:free",
        "anthracite-org/magnum-v4-72b:free"
    ]

    # --- Vault Security ---
    VAULT_MASTER_KEY = os.getenv("VAULT_MASTER_KEY")

    # --- RabbitMQ Configuration ---
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
    RABBITMQ_QUEUE_MISSION_REQUESTS = "mission_requests"
    RABBITMQ_QUEUE_MISSION_STATUS = "mission_status"

    # --- Agent Settings ---
    DEFAULT_TRUST_SCORE_THRESHOLD = 70
    MAX_RETRY_ATTEMPTS = 3
    TRACE_DIR = "data/traces"
    PROFILE_DIR = "data/profiles"
    KNOWLEDGE_BASE_PATH = "data/knowledge_base.json"
    VAULT_PATH = "data/vault/vault.enc"

    # --- UI Settings ---
    UI_PORT = 8501

    # --- Logging ---
    LOG_DIR = "logs"
    AGENT_LOG_FILE = os.path.join(LOG_DIR, "agent.log")
    UI_LOG_FILE = os.path.join(LOG_DIR, "ui.log")

    # Ensure directories exist
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(TRACE_DIR, exist_ok=True)
    os.makedirs(PROFILE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(KNOWLEDGE_BASE_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(VAULT_PATH), exist_ok=True)


