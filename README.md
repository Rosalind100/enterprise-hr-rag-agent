<div align="center">

# 企业级 HR 智能问答系统
**Enterprise HR RAG Agent**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-yellow.svg)](https://python.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorDB-purple.svg)](https://www.trychroma.com/)

*基于 LangChain + ChromaDB + DeepSeek 构建的垂直领域知识库 RAG 智能问答系统*
</div>

---

## 项目背景与痛点解决
传统企业内部存在大量的人事制度、考勤、报销等长文档（如几百页 PDF），员工查找困难，HR 重复答疑成本极高。同时，直接使用大模型进行全量问答存在**高昂的 Token 成本**与**严重的“幻觉”问题**。

本项目基于开源架构进行了深度重构与二次开发，通过引入**双路路由机制**与**意图识别分类检索**，在保证回答准确率的同时，彻底解决了企业落地的成本与幻觉痛点。

---

## 核心重构亮点

### 1. 双路智能路由架构（降本增效）
- **本地极速拦截**：针对高频、固定的短文本问题（如考勤打卡），直接匹配本地字典进行毫秒级响应，实现 0 Token 消耗。
- **长句动态放行**：针对长文本、复杂逻辑的提问，自动放行至 RAG 链路交由大模型深度推理，避免因本地拦截机制过于死板而导致的答非所问。

### 2. 防幻觉与 Metadata 精准过滤
- **意图识别前置**：在执行检索前，首先通过 LLM 判断用户意图，将其归类至入职、考勤、请假、报销或闲聊。
- **定向分类检索**：结合 ChromaDB 的 `Metadata` 标签，仅在对应的分类库（如 `expense`）中进行向量相似度检索，杜绝跨部门知识污染。

### 3. 企业级前端交互重构
- **UI 深度定制**：手写自定义 CSS 覆盖 Streamlit 默认样式，实现现代大厂极简设计；固定独立滚动聊天视窗与悬浮底部输入框。
- **Markdown 安全清洗**：重写渲染逻辑，解决大模型输出乱码（星号）问题，并加入 `HTML.escape` 防范 XSS 注入。
- **实时数据看板**：右侧动态统计 FAQ 与 RAG 的命中/检索频次，直观展示系统运行状态。

### 4. 工程化落地与安全隔离
- **知识库生命周期管理**：重构底层数据加载逻辑，实现向量数据的“一键同步与全量重建”，彻底解决因文档频繁迭代导致的旧缓存残留与检索异常问题，保障知识库的高可用性。
- **多层级安全隔离架构**：采用动态环境注入机制，实现核心通信凭证与代码逻辑的物理分离；配合版本控制系统的防泄露拦截策略，从源头阻断敏感信息外泄；同时在渲染层加入 XSS 防御，保障系统端到端的安全。

---

## 核心技术栈
| 领域 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **前端展示** | Streamlit / HTML / CSS | 极简聊天交互与数据看板展示 |
| **后端框架** | FastAPI / Uvicorn / Pydantic | 提供标准 RESTful API，自动数据校验 |
| **AI 编排框架** | LangChain | 构建 Prompt 模板、意图识别链与 RAG 检索链 |
| **大语言模型** | DeepSeek API | 意图分类判断与最终答案归纳生成 |
| **向量化模型** | 阿里云 DashScope Embedding | 文本切片转向量矩阵 |
| **向量数据库** | ChromaDB (本地持久化) | 文档分片存储与 Metadata 定向过滤 |

---

## 本地部署指南

**1. 安装依赖**
在终端执行 pip 安装命令，拉取项目所需的所有依赖包。

**2. 初始化系统配置**
在本地配置好运行所需的 API 凭证与系统参数，确保网络通信与模型调用的安全隔离。

**3. 重建本地向量知识库**
首次运行必做，在终端执行程序清空旧缓存并重新将文档向量化。

**4. 启动前后端服务**
分别开启后端接口服务与前端交互页面，即可在浏览器中通过 UI 界面进行问答体验。

---

## 核心目录结构说明

```text
📁 HR-RAG-Agent
├── 📂 docs/
│   └── 📂 knowledge/          # 存放人事制度的原始 TXT/PDF 文档
├── 📂 src/                    # 核心 AI 逻辑与工具模块
│   ├── 📄 faq.py              # 本地极速问答匹配逻辑
│   ├── 📄 chains.py           # 意图识别与 RAG 检索主链
│   ├── 📄 knowledge_base.py   # 向量库加载与 Metadata 分类检索
│   └── 📄 prompts.py          # 严格约束大模型的提示词工程
├── 📄 main.py                 # 向量库强制重建与控制台测试入口
├── 📄 app.py                  # FastAPI 后端接口服务入口
└── 📄 ui.py                   # Streamlit 极简前端交互页面
