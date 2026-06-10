from langchain_core.runnables import RunnableLambda
from src.chains import build_rag_chain
from src.faq import get_faq_reply
from src.knowledge_base import get_vector_db
from src.logger import logger

def build_faq_rag_chain():
    """FAQ + RAG 组合链"""
    try:
        logger.info("构建FAQ-RAG组合链")
        vector_db = get_vector_db()
        rag_chain = build_rag_chain(vector_db)

        def interceptor(inputs):
            """拦截器：优先匹配FAQ，再走RAG"""
            try:
                query = inputs.get("query", "") if isinstance(inputs, dict) else inputs
                faq_ans = get_faq_reply(query)
                if faq_ans:
                    logger.info("FAQ拦截成功")
                    return faq_ans
                return rag_chain.invoke(inputs)
            except Exception as e:
                logger.error(f"拦截器异常：{str(e)}")
                return "服务异常，请稍后再试~"

        return RunnableLambda(interceptor)
    except Exception as e:
        logger.error(f"组合链构建失败：{str(e)}")
        raise