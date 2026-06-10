import os
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

        # 初始化向量库
        try:
            if not os.path.exists(CHROMA_PATH):
                logger.info("首次启动，创建向量库")
                docs = load_docs_with_metadata()
                split_docs_list = split_docs(docs)
                db = get_vector_db(split_docs_list)
            else:
                db = get_vector_db()
        except Exception as e:
            logger.critical(f"向量库初始化失败：{str(e)}", exc_info=True)
            print("❌ 启动失败：向量库异常")
            exit(1)

        # 构建RAG链
        try:
            rag_chain = build_rag_chain(db)
            logger.info("✅ 系统初始化完成")
        except Exception as e:
            logger.critical(f"RAG链构建失败：{str(e)}", exc_info=True)
            print("❌ 启动失败：RAG链异常")
            exit(1)

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
                    print("助手：输入不能为空~")
                    continue
                if user_input.lower() == "quit":
                    print("再见！")
                    logger.info("用户退出程序")
                    break

                # 新增：向量库操作指令（测试用）
                if user_input.startswith("添加文档:"):
                    file_path = user_input.replace("添加文档:", "").strip()
                    if add_doc_to_vector_db(file_path):
                        print("助手：✅ 文档添加成功！")
                    else:
                        print("助手：❌ 文档添加失败！")
                    continue
                if user_input.startswith("删除文档:"):
                    file_name = user_input.replace("删除文档:", "").strip()
                    if delete_doc_from_vector_db(file_name):
                        print("助手：✅ 向量删除成功！")
                    else:
                        print("助手：❌ 向量删除失败！")
                    continue
                if user_input == "清空向量库":
                    reset_vector_db()
                    print("助手：✅ 向量库已清空！")
                    continue

                # FAQ匹配
                faq_ans = get_faq_reply(user_input)
                if faq_ans:
                    print(f"\n助手：{faq_ans}")
                    chat_history.append(f"用户：{user_input}")
                    chat_history.append(f"助手：{faq_ans}")
                    continue

                # RAG回答
                res = rag_chain.invoke({
                    "query": user_input,
                    "history": "\n".join(chat_history[-6:]) if chat_history else ""
                })
                print(f"\n助手：{res}")

                # 记录历史
                chat_history.append(f"用户：{user_input}")
                chat_history.append(f"助手：{res}")

            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                logger.error(f"对话异常：{str(e)}", exc_info=True)
                print("\n助手：服务异常，请稍后再试~")

    except Exception as e:
        logger.critical(f"全局启动失败：{str(e)}", exc_info=True)
        print("❌ 程序启动失败，请查看日志")
        exit(1)