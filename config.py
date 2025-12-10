import os
import logging

# Disable Telemetry
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
    "gpt-oss:20b-100K",
    "gemma3:12b-100K",
    "qwen3:14b-100K"
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
EXP1_NEEDLE_POSITIONS = ["start", "middle", "end"]
EXP2_DOC_COUNTS = [2, 5, 10, 20, 50]
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

formatter = PathSanitizerFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(os.path.join(RESULTS_DIR, "benchmark.log"))
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger("Benchmark")
