"""全局资源管理：单例化向量库、RAG链，避免重复初始化"""
from typing import Optional
from src.knowledge_base import get_vector_db, load_docs_with_metadata, split_docs
from src.chains import build_rag_chain
from src.chain_wrapper import build_faq_rag_chain
from src.logger import logger
from src.config import settings
import os

# 全局资源对象
_vector_db: Optional[object] = None
_rag_chain: Optional[object] = None
_faq_rag_chain: Optional[object] = None

def init_global_resources():
    """初始化全局资源（仅执行一次）"""
    global _vector_db, _rag_chain, _faq_rag_chain
    try:
        # 初始化向量库
        if _vector_db is None:
            logger.info("初始化全局向量库")
            if not os.path.exists(settings.CHROMA_PATH):
                docs = load_docs_with_metadata()
                split_docs_list = split_docs(docs)
                _vector_db = get_vector_db(split_docs_list)
            else:
                _vector_db = get_vector_db()
        
        # 初始化RAG链
        if _rag_chain is None:
            logger.info("初始化全局RAG链")
            _rag_chain = build_rag_chain(_vector_db)
        
        # 初始化FAQ+RAG组合链
        if _faq_rag_chain is None:
            logger.info("初始化全局FAQ-RAG组合链")
            _faq_rag_chain = build_faq_rag_chain()
        
        logger.info("✅ 全局资源初始化完成")
    except Exception as e:
        logger.error(f"全局资源初始化失败：{str(e)}", exc_info=True)
        raise

def get_vector_db_instance():
    """获取向量库单例"""
    if _vector_db is None:
        init_global_resources()
    return _vector_db

def get_rag_chain_instance():
    """获取RAG链单例"""
    if _rag_chain is None:
        init_global_resources()
    return _rag_chain

def get_faq_rag_chain_instance():
    """获取FAQ+RAG组合链单例"""
    if _faq_rag_chain is None:
        init_global_resources()
    return _faq_rag_chain