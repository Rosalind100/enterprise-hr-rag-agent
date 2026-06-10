import os

# 项目路径固定为hr-rag-helper内
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# 文档目录 & 向量库目录
DOC_PATH = os.path.join(PROJECT_ROOT, "docs", "knowledge")
CHROMA_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

# 确保目录存在
os.makedirs(DOC_PATH, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)

# 模型配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
EMBEDDING_MODEL = "text-embedding-v1"

LLM_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY"),
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
    "temperature": 0.1
}

# 文档分片配置（统一管理）
CHUNK_SIZE = 200
CHUNK_OVERLAY = 30