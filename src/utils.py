from .logger import logger
import os

def get_start_opening():
    """欢迎语"""
    return """
🏢 人事制度问答助手
快捷提问：入职材料 | 补卡流程 | 报销标准 | 请假流程
输入 quit 退出对话
"""

def empty_answer_guard():
    """无答案兜底"""
    logger.warning("触发无答案兜底回复")
    return "抱歉，未查询到相关信息，请您咨询HR部门~"

def validate_file_path(file_path):
    """验证文件路径是否存在"""
    if not os.path.exists(file_path):
        logger.error(f"文件不存在：{file_path}")
        return False
    if not os.path.isfile(file_path):
        logger.error(f"不是文件：{file_path}")
        return False
    return True