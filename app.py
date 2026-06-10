# app.py
import os
import warnings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))

warnings.filterwarnings("ignore")

from src.knowledge_base import get_vector_db
from src.chains import build_rag_chain
from src.faq import get_faq_reply
from src.logger import logger
from src.config import CHROMA_PATH

# ========== FastAPI 应用初始化 ==========
app = FastAPI(
    title="人事制度问答助手 API",
    description="基于 RAG 的人事制度智能问答接口，支持 FAQ 缓存 + 分类检索 + 意图识别",
    version="1.0.0"
)

# ========== 全局资源（启动时初始化） ==========
rag_chain = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化向量库和 RAG 链"""
    global rag_chain
    try:
        logger.info("🚀 FastAPI 服务启动，初始化资源...")
        
        # 1. 检查向量库是否存在
        if not os.path.exists(CHROMA_PATH):
            error_msg = f"向量库目录不存在：{CHROMA_PATH}，请先运行 main.py 构建向量库。"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # 2. 加载已有向量库
        db = get_vector_db()
        logger.info("✅ 向量库加载成功")
        
        # 3. 构建 RAG 链
        rag_chain = build_rag_chain(db)
        logger.info("✅ RAG 链构建成功")
        
        logger.info("🎉 服务启动完成，等待请求...")
    except Exception as e:
        logger.critical(f"服务启动失败：{str(e)}", exc_info=True)
        raise

# ========== 请求/响应模型 ==========
class ChatRequest(BaseModel):
    query: str = Field(..., description="用户问题", min_length=1)
    history: Optional[str] = Field(None, description="历史对话（多轮用换行分隔）")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="助手回复")
    source: str = Field("rag", description="答案来源：faq / rag")

# ========== 健康检查 ==========
@app.get("/health", summary="健康检查")
async def health_check():
    return {"status": "ok", "rag_chain_ready": rag_chain is not None}

# ========== 核心问答接口 ==========
@app.post("/chat", response_model=ChatResponse, summary="问答接口")
async def chat(request: ChatRequest):
    """
    接收用户问题，返回答案。
    流程：先查 FAQ 缓存，命中则直接返回；否则调用 RAG 链生成答案。
    """
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        history = request.history or ""
        logger.info(f"收到请求：{query}")
        
        # 1. 尝试 FAQ 匹配
        faq_answer = get_faq_reply(query)
        if faq_answer:
            logger.info(f"FAQ 命中，直接返回")
            return ChatResponse(answer=faq_answer, source="faq")
        
        # 2. 未命中 FAQ，调用 RAG 链
        if rag_chain is None:
            raise HTTPException(status_code=503, detail="RAG 链未初始化")
        
        result = rag_chain.invoke({
            "query": query,
            "history": history
        })
        
        logger.info(f"RAG 生成答案长度：{len(result)}")
        return ChatResponse(answer=result, source="rag")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"请求处理异常：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务内部错误，请查看日志")