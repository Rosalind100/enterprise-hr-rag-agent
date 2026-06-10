# HR 人事制度 RAG 智能问答助手
基于 LangChain + Chroma 向量库 + DeepSeek 大模型 + FastAPI 搭建的**企业人事制度智能问答系统**。
支持「本地控制台交互」和「HTTP 接口调用」两种运行模式，采用 **FAQ 快速应答 + RAG 分类检索** 双架构，具备意图识别、闲聊拦截、多轮对话、全链路日志、异常容错等企业级能力。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/Framework-LangChain-orange)](https://www.langchain.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green)](https://fastapi.tiangolo.com/)
[![VectorDB](https://img.shields.io/badge/VectorDB-Chroma-purple)](https://www.trychroma.com/)

## 📌 项目简介
本系统专为企业人事场景设计，聚焦**入职、考勤、请假、差旅报销**四大核心制度问答：
1. 高频固定问题走本地 FAQ 缓存，毫秒级响应，大幅节省大模型 Token 与接口费用；
2. 复杂/低频问题走 RAG 知识库，结合**意图识别 + 分类检索**，精准缩小检索范围，杜绝答非所问；
3. 全链路日志记录、全局异常捕获，服务长期运行稳定不崩溃；
4. 支持本地控制台测试 + 标准 RESTful 接口，可无缝对接内部系统、前端页面、小程序。

## ✨ 核心功能
### 1. 问答核心能力
- ✅ **FAQ 极速应答**：关键词匹配高频人事问题，不调用大模型，响应无延迟
- ✅ **意图智能识别**：自动区分 入职/考勤/请假/报销/无关闲聊 5 类意图
- ✅ **分类精准检索**：根据意图定向查询对应知识库，提升检索准确率
- ✅ **多轮上下文对话**：支持连续追问，自动管理对话历史
- ✅ **闲聊自动拦截**：非人事类问题统一引导回复，限定问答边界

### 2. 文档 & 向量库能力
- ✅ 多格式文档支持：`TXT / PDF / DOCX`，PDF 逐页解析防崩溃
- ✅ 向量库全操作：支持文档新增、删除、全量清空、重建
- ✅ 文档元数据管理：自动绑定文档分类、文件名、更新时间

### 3. 运维 & 容错能力
- ✅ 双路日志：控制台打印 + 本地日志文件，日志自动轮转切割
- ✅ 全场景异常捕获：密钥失效、文档缺失、网络异常、非法输入均友好提示
- ✅ 启动自检：服务启动前自动校验向量库、模型配置

### 4. 接口服务能力（FastAPI）
- ✅ 标准 RESTful 接口，自动生成交互式接口文档
- ✅ 严格参数校验、统一请求/响应格式
- ✅ 答案来源标记（区分 FAQ / RAG），便于问题排查

## 🛠️ 技术栈
- 编程语言：Python 3.8+
- RAG 框架：LangChain
- 向量数据库：Chroma（本地持久化，数据安全）
- 嵌入模型：阿里云通义千问 `text-embedding-v1`
- 大语言模型：DeepSeek `deepseek-chat`
- Web 接口：FastAPI
- 文档解析：pdfplumber、docx2txt
- 环境管理：python-dotenv

## 📁 项目目录结构
hr-rag-helper/
├── .env # 环境变量（存放模型 API 密钥，需手动创建）
├── main.py # 本地控制台问答入口
├── app.py # FastAPI 接口服务入口
├── requirements.txt # 项目依赖清单
├── README.md # 项目说明文档
├── chroma_db/ # 自动生成：Chroma 向量库存放目录
├── logs/ # 自动生成：全流程日志目录
├── docs/
│ └── knowledge/ # 人事知识库目录（存放制度文档）
│ ├── 入职流程.txt
│ ├── 考勤制度.txt
│ ├── 请假制度.txt
│ └── 差旅报销.txt
└── src/ # 核心代码包
├── init.py # Python 包标识文件（必需）
├── config.py # 全局路径、模型、参数统一配置
├── logger.py # 全局日志模块
├── utils.py # 通用工具函数
├── knowledge_base.py # 文档加载、分片、向量库、分类检索逻辑
├── llm.py # DeepSeek 大模型实例封装
├── prompts.py # 提示词模板 + 固定兜底回复
├── faq.py # 高频问题 FAQ 匹配逻辑
├── chains.py # 意图识别链 + RAG 主业务链
└── chain_wrapper.py # FAQ+RAG 组合链（扩展预留）
plaintext

## ⚙️ 前置环境准备
### 1. 虚拟环境（推荐）
隔离项目依赖，避免版本冲突：
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate
2. 安装依赖
pip install -r requirements.txt
3. 配置环境变量（关键步骤）
在项目根目录新建 .env 文件，填入两大模型平台密钥（缺一不可）：
env
# 阿里云通义千问 嵌入模型密钥
DASHSCOPE_API_KEY=你的通义千问API_KEY

# DeepSeek 大模型密钥
DEEPSEEK_API_KEY=你的DeepSeek API_KEY
密钥获取地址：
通义千问：https://dashscope.console.aliyun.com/
DeepSeek：https://platform.deepseek.com/
4. 知识库文档规范
所有人事制度文档统一放置在 docs/knowledge/ 目录：
优先使用 UTF-8 编码 TXT 格式，兼容 PDF、DOCX；
文件名需与 src/knowledge_base.py 中 DOC_CATEGORY_MAP 映射表对应，否则分类检索失效。
表格
文档名称	分类标签	对应意图	业务场景
入职流程.txt	entry	1	入职材料、报到、试用期
考勤制度.txt	attend	2	打卡、迟到、补卡
请假制度.txt	leave	3	年假、事假、病假、婚假
差旅报销.txt	expense	4	出差标准、发票、报销
🚀 项目运行（两种模式）
⚠️ 重要前置规则：首次运行 / 更新知识库后，必须先执行控制台模式生成向量库，再启动 FastAPI 接口！
模式一：本地控制台交互（测试 / 初始化向量库）
python main.py
运行成功后功能：
直接输入问题进行问答；
内置指令：添加文档:文件路径 / 删除文档:文件名 / 清空向量库；
输入 quit 正常退出程序。
模式二：FastAPI 接口服务（线上 / 对接第三方系统）
1. 启动命令
# 开发环境（热重载，修改代码自动重启）
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 生产环境（稳定运行，关闭热重载）
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2
2. 访问自动接口文档
服务启动后，浏览器打开地址即可在线测试接口：
交互式文档：http://127.0.0.1:8000/docs
简易文档：http://127.0.0.1:8000/redoc
🔌 FastAPI 接口详细说明
1. 健康检查接口
请求方式：GET
接口地址：/health
作用：检测服务状态、RAG 链是否初始化完成
调用示例：
curl http://127.0.0.1:8000/health
正常响应：
json
{"status":"ok","rag_chain_ready":true}
2. 核心问答接口（主接口）
请求方式：POST
接口地址：/chat
逻辑流程：优先匹配 FAQ → 未命中则调用 RAG 知识库
请求参数说明
表格
参数名	类型	是否必填	说明
query	string	是	用户提问内容，非空校验
history	string	否	多轮对话历史，使用 \n 换行分隔；单轮对话传 null/ 空字符串
示例 1：单轮对话（无历史）
请求体：
json
{
  "query": "入职需要准备什么材料",
  "history": null
}
响应（FAQ 命中）：
json
{
  "answer": "1.身份证原件及复印件2份；2.学历证书原件及复印件；3.一寸白底照片2张；4.本人银行卡。",
  "source": "faq"
}
示例 2：多轮对话（带上下文）
JSON 中换行需使用转义符 \n：
json
{
  "query": "还有其他要求吗？",
  "history": "用户：入职需要准备什么材料\n助手：1.身份证原件及复印件2份；2.学历证书原件及复印件；3.一寸白底照片2张；4.本人银行卡。"
}
Curl 调用示例
curl -X POST "http://127.0.0.1:8000/chat" \
-H "Content-Type: application/json" \
-d '{
  "query": "迟到怎么处理",
  "history": ""
}'
📝 知识库更新流程
如需新增 / 修改人事制度文档，按以下步骤操作：
将新文档放入 docs/knowledge/ 目录；
新文件名需同步更新 src/knowledge_base.py 中的 DOC_CATEGORY_MAP 映射；
删除项目根目录 chroma_db 文件夹（清除旧向量库）；
执行 python main.py 重建向量库；
重启 FastAPI 服务即可生效。
📜 日志说明
日志路径：项目根目录 logs/hr_rag_helper.log
日志规则：单文件最大 50MB，自动轮转，最多保留 5 份历史日志
日志内容：服务启动日志、问答记录、检索详情、异常堆栈，用于故障排查
❗ 常见问题 & 故障排查
导入报错 ImportError
原因：src 缺少 __init__.py 或运行目录非项目根目录；
解决：补充空的 src/__init__.py，在项目根目录执行命令。
FastAPI 启动提示「向量库不存在」
原因：未初始化向量库；
解决：先运行 python main.py 生成 chroma_db 目录。
分类检索不生效
原因：旧向量库无元数据 / 文档名与映射表不匹配；
解决：删除 chroma_db 重建，核对 DOC_CATEGORY_MAP。
模型初始化失败
原因：.env 密钥错误、网络无法访问模型接口；
解决：核对 API 密钥，检查网络连通性。
🚀 后续拓展方向
实现文档增量更新，无需全量重建向量库；
新增接口鉴权（API Key / JWT），提升接口安全性；
接入 Redis 缓存热点问题、持久化多用户对话；
开发 Web 可视化前端页面；
增加接口限流，防护恶意请求；
接入 LangSmith 实现全链路调用追踪。
