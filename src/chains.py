from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from src.llm import get_llm
from src.prompts import INTENT_PROMPT, ANSWER_PROMPT, IRRELEVANT_REPLY
from .knowledge_base import get_retriever_by_category, INTENT_TO_CATEGORY
from .logger import logger
import os

# 意图识别链
def get_intent_chain():
    try:
        llm = get_llm()
        chain = INTENT_PROMPT | llm | StrOutputParser()
        logger.info("✅ 意图识别链初始化成功")
        return chain
    except Exception as e:
        logger.error(f"意图链初始化失败：{str(e)}")
        raise

intent_chain = get_intent_chain()

def build_rag_chain(vector_db):
    """构建RAG主链（适配分类检索）"""
    try:
        logger.info("✅ 分类检索模式就绪")

        def format_docs(docs):
            """格式化检索到的文档"""
            try:
                if not docs:
                    logger.warning("⚠️ 当前分类下未检索到任何文档，请检查向量库是否已正确构建")
                    return "无相关资料"
                # 打印命中的文档信息（调试用）
                for idx, doc in enumerate(docs):
                    file_name = os.path.basename(doc.metadata.get("source", ""))
                    cat = doc.metadata.get("category", "")
                    logger.info(f"  命中文档{idx+1}：{file_name} | 分类：{cat} | 长度：{len(doc.page_content)}字")
                return "\n\n".join(d.page_content for d in docs)
            except Exception as e:
                logger.error(f"文档格式化失败：{str(e)}")
                return "无相关资料"

        def full_flow(inputs):
            """完整RAG流程"""
            try:
                query = inputs.get("query", "").strip()
                history = inputs.get("history", "无")

                if not query:
                    logger.warning("用户输入为空")
                    return "请输入有效的问题~"
                logger.info(f"处理查询：{query}")

                # 1. 意图识别
                try:
                    intent = intent_chain.invoke({"query": query}).strip()
                    logger.info(f"意图识别结果：{intent}")
                except Exception as e:
                    logger.error(f"意图识别失败：{str(e)}")
                    return IRRELEVANT_REPLY

                # 2. 无关问题直接返回
                if intent == "5" or intent not in ["1", "2", "3", "4"]:
                    return IRRELEVANT_REPLY

                # 3. 按意图检索对应分类的文档
                target_category = INTENT_TO_CATEGORY[intent]
                retriever = get_retriever_by_category(vector_db, target_category)
                docs = retriever.invoke(query)
                logger.info(f"检索到 {len(docs)} 条【{target_category}】分类文档")
                if len(docs) == 0:
                    logger.warning(f"⚠️ 向量库中 category={target_category} 的文档为 0 条！请运行 main.py 重建向量库。")
                context = format_docs(docs)

                # 4. 生成回答
                llm = get_llm()
                ans_chain = ANSWER_PROMPT | llm | StrOutputParser()
                result = ans_chain.invoke({
                    "query": query,
                    "context": context,
                    "history": history
                })
                logger.info("✅ 回答生成成功")
                return result

            except Exception as e:
                logger.error(f"查询处理失败：{str(e)}")
                return "非常抱歉，处理问题时发生错误，请稍后再试~"

        return RunnableLambda(full_flow)

    except Exception as e:
        logger.error(f"RAG链构建失败：{str(e)}")
        raise ValueError("RAG链构建异常") from e