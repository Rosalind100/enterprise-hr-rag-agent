from .logger import logger

FAQ_CACHE = {
    "入职需要准备什么材料": "1.身份证原件及复印件2份；2.学历证书原件及复印件；3.一寸白底照片2张；4.本人银行卡。",
    "入职报到时间地点": "上午9点，公司总部3楼HR办公室，无法按时报到请提前告知HR。",
    "试用期多长时间": "试用期3个月，薪资为转正80%，期满3个工作日内通知结果。",
    "补卡流程": "当天向直属上级报备，系统补签，每月最多3次。",
    "迟到处理": "每月3次内不扣薪，超出每次扣绩效50元。",
    "差旅报销标准是什么": "交通经济舱/二等座；住宿一线400/晚，其余300/晚；餐补80元/天。",
    "报销发票丢了怎么办": "联系商家补开电子票，无法补开填写说明签字上交。",
    "报销多久到账": "审批通过后5个工作日内到账。"
}

def get_faq_reply(msg):
    """FAQ快速匹配"""
    try:
        if not msg:
            logger.warning("FAQ入参为空")
            return None
        
        msg = msg.strip().lower()
        logger.debug(f"FAQ匹配：{msg}")

        # 1. 入职相关
        if "入职" in msg or "报到" in msg:
            if any(i in msg for i in ["材料", "准备", "带", "拿", "东西"]):
                logger.info("FAQ命中：入职材料")
                return FAQ_CACHE["入职需要准备什么材料"]
            if any(i in msg for i in ["地点", "时间", "几点", "哪里"]):
                logger.info("FAQ命中：入职报到")
                return FAQ_CACHE["入职报到时间地点"]

        # 2. 考勤相关
        if any(i in msg for i in ["补卡", "忘记打卡", "漏打卡"]):
            logger.info("FAQ命中：补卡")
            return FAQ_CACHE["补卡流程"]
        if any(i in msg for i in ["迟到", "晚到", "打卡晚", "扣钱"]):
            logger.info("FAQ命中：迟到")
            return FAQ_CACHE["迟到处理"]

        # 3. 报销/差旅相关
        if any(i in msg for i in ["报销", "差旅", "出差", "住宿", "餐补", "补贴"]):
            # 【必须是这行！】如果字数超过 15，放行
            if len(msg) > 15:
                logger.info("长句放行：跳过 FAQ，交由 RAG 处理")
                return None
                
            if any(i in msg for i in ["丢", "没票", "发票"]):
                logger.info("FAQ命中：报销发票")
                return FAQ_CACHE["报销发票丢了怎么办"]
            if any(i in msg for i in ["到账", "多久", "几天"]):
                logger.info("FAQ命中：报销到账")
                return FAQ_CACHE["报销多久到账"]
            
            logger.info("FAQ命中：差旅标准")
            return FAQ_CACHE["报销发票丢了怎么办"]

        logger.info("FAQ未命中")
        return None

    except Exception as e:
        logger.error(f"FAQ匹配异常：{str(e)}", exc_info=True)
        return None