import os
import shutil
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))
from src.config import CHROMA_PATH
from src.knowledge_base import (
    load_docs_with_metadata, get_vector_db, split_docs,
    add_doc_to_vector_db, delete_doc_from_vector_db, reset_vector_db
)
from src.chains import build_rag_chain
from src.faq import get_faq_reply
from src.logger import logger
from src.utils import get_start_opening

if __name__ == "__main__":
    try:
        logger.info("==== 人事制度问答助手 启动 ====")

        # 【强制清空旧库】
        logger.info(">>> 正在强制清空旧向量库 <<<")
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH, ignore_errors=True)
        logger.info(">>> 旧库已删除，准备重新加载文档 <<<")

        # 【强制读取文档并重建】
        docs = load_docs_with_metadata()
        if not docs:
            logger.error(">>> 致命错误：没有读取到任何文档！请检查 docs/knowledge/ 目录和文件名！ <<<")
            exit(1)
            
        split_docs_list = split_docs(docs)
        db = get_vector_db(split_docs_list)
        logger.info(">>> 向量库重建完成，准备进入对话 <<<")

        # 构建RAG链
        rag_chain = build_rag_chain(db)
        logger.info("✅ 系统初始化完成")

        # 对话循环
        first_flag = True
        chat_history = []

        while True:
            if first_flag:
                print("\n" + get_start_opening())
                first_flag = False

            try:
                user_input = input("\n请输入问题：").strip()
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    print("再见！")
                    break

                faq_ans = get_faq_reply(user_input)
                if faq_ans:
                    print(f"\n助手：{faq_ans}")
                    chat_history.append(f"用户：{user_input}")
                    chat_history.append(f"助手：{faq_ans}")
                    continue

                res = rag_chain.invoke({
                    "query": user_input,
                    "history": "\n".join(chat_history[-6:]) if chat_history else ""
                })
                print(f"\n助手：{res}")
                chat_history.append(f"用户：{user_input}")
                chat_history.append(f"助手：{res}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"对话异常：{str(e)}", exc_info=True)
                print("\n助手：服务异常，请稍后再试~")

    except Exception as e:
        logger.critical(f"全局启动失败：{str(e)}", exc_info=True)
        print(f"❌ 程序启动失败：{e}")