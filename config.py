import os
import logging

# Environment Setup
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["SCARF_NO_ANALYTICS"] = "true"
os.environ["DO_NOT_TRACK"] = "true"
os.environ["NOMIC_TELEMETRY_OPT_OUT"] = "true"

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
if not OLLAMA_HOST.startswith("http"):
    OLLAMA_HOST = f"http://{OLLAMA_HOST}"

# Models to benchmark
MODELS = [
    "llama3.2:3b-100K",
    "granite3.3:2b-100K",
    "gemma3:4b-100K",
    "qwen3:4b-100K",
    "gemma3:12b-100K",
    "qwen3:14b-100K",
    "gpt-oss:20b-100K",
]

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")
ENGLISH_ARTICLES_DIR = os.path.join(DOCUMENTS_DIR, "articles_english")
HEBREW_ARTICLES_DIR = os.path.join(DOCUMENTS_DIR, "articles_hebrew")
METADATA_FILE = os.path.join(DOCUMENTS_DIR, "articles_metadata.json")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")

# Ensure directories exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# Experiment Settings
SEED = 42

# Experiment 1: Needle in Haystack
EXP1_NEEDLE_POSITIONS = ["start", "middle", "end"]
EXP1_DETAILED_POSITIONS = ["control", "start", "middle", "end"]
EXP1_DETAILED_PROMPT_LENGTHS = [5000, 10000, 50000, 100000, 150000, 200000]

# Needle experiment configurations
NEEDLE_EXPERIMENTS = {
    "quick": {
        "fact": "The secret code is BLUE-ZEBRA-99.",
        "question": "What is the secret code mentioned in the text? Return only the code.",
        "expected_answer": "BLUE-ZEBRA-99",
        "context_words": 50000,
        "positions": EXP1_NEEDLE_POSITIONS,
        "use_articles": True,
    },
    "info_retrieval": {
        "secret_message": (
            "In the twilight of forgotten ages walked Vramiel, ancient prince "
            "of the kingdom of Elel-Em, whose voice bore the echo of dawn."
        ),
        "question": "Who was the prince of Elel-Em?",
        "expected_answer": "VRAMIEL",
        "source_file": "lotr",
        "prompt_lengths": EXP1_DETAILED_PROMPT_LENGTHS,
        "positions": EXP1_DETAILED_POSITIONS,
    },
    "anomaly_detection": {
        "secret_message": "To enable god-mode, type 'DQDDI'.",
        "question": "What special code or instruction, if any, is mentioned in the text for enabling god-mode?",
        "expected_answer": "DQDDI",
        "source_file": "lotr",
        "prompt_lengths": EXP1_DETAILED_PROMPT_LENGTHS,
        "positions": EXP1_DETAILED_POSITIONS,
    },
}

# Experiment 2: Context Size
EXP2_DOC_COUNTS = [2, 5, 10, 20, 50]
EXP2_ID_RANGE = (1000, 9999)

# Experiment 3: RAG
EXP3_RAG_K = 3
EXP3_CHUNK_SIZE = 500


# Logging Setup
class PathSanitizerFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        # Replace the absolute BASE_DIR with just the folder name (relative path) to hide PII
        if BASE_DIR in msg:
            msg = msg.replace(BASE_DIR, os.path.basename(BASE_DIR))
        return msg


formatter = PathSanitizerFormatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler(os.path.join(RESULTS_DIR, "benchmark.log"))
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
logger = logging.getLogger("Benchmark")


def validate_config():
    """Validate configuration settings."""
    if not os.path.exists(ENGLISH_ARTICLES_DIR):
        logger.warning(f"English articles directory not found: {ENGLISH_ARTICLES_DIR}")

    if not os.path.exists(HEBREW_ARTICLES_DIR):
        logger.warning(f"Hebrew articles directory not found: {HEBREW_ARTICLES_DIR}")

    # We won't block execution if Ollama is down, but we'll warn
    # (Checking connection can be slow, so maybe just check formatted URL)
    if not OLLAMA_HOST.startswith("http"):
        logger.warning(f"Ollama host might be malformed: {OLLAMA_HOST}")


# Call at module load to verify setup
validate_config()
