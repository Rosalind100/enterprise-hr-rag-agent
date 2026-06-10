from langchain_openai import ChatOpenAI
from .config import LLM_CONFIG
from .logger import logger

def get_llm():
    """获取LLM模型实例"""
    try:
        if not LLM_CONFIG["api_key"]:
            logger.error("DEEPSEEK_API_KEY 未配置")
            raise ValueError("请配置LLM API Key")
        
        llm = ChatOpenAI(
            api_key=LLM_CONFIG["api_key"],
            base_url=LLM_CONFIG["base_url"],
            model=LLM_CONFIG["model"],
            temperature=LLM_CONFIG["temperature"]
        )
        logger.info("✅ LLM模型初始化成功")
        return llm
    except Exception as e:
        logger.error(f"LLM初始化失败：{str(e)}", exc_info=True)
        raise ValueError("LLM模型初始化异常") from e

# 兼容原有代码
llm = get_llm()