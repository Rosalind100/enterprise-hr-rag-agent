import os
import shutil
import pdfplumber
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
# 🔥 安全导入：只导入需要的加载器，不导入DirectoryLoader（卡死根源）
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.document_loaders import PDFPlumberLoader
from .config import DOC_PATH, CHROMA_PATH, DASHSCOPE_API_KEY, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAY
from .logger import logger
from .utils import validate_file_path
from docx import Document as DocxDocument  # 处理Word文档用

# ===================== 文档 & 分类映射 =====================
DOC_CATEGORY_MAP = {
    "入职流程.txt": "entry",
    "考勤制度.txt": "attend",
    "请假制度.txt": "leave",
    "差旅报销.txt": "expense",
    "入职流程.pdf": "entry",
    "考勤制度.pdf": "attend",
    "请假制度.pdf": "leave",
    "差旅报销.pdf": "expense"
}

# 意图 → 检索分类映射
INTENT_TO_CATEGORY = {
    "1": "entry",
    "2": "attend",
    "3": "leave",
    "4": "expense",
    "5": "other"
}

# ===================== PDF读取优化 =====================
# ===================== PDF读取优化（3层防崩溃版 · 极简修改） =====================
def load_single_pdf(file_path):
    """优化PDF读取：逐页解析+跳空页+防崩溃，内存占用极低"""
    try:
        if not validate_file_path(file_path):
            return []
        
        docs = []
        # 🔥 核心优化1：逐页读取PDF，读一页释一页，不一次性加载整个文件
        with pdfplumber.open(file_path) as pdf:
            file_name = os.path.basename(file_path)
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # 🔥 核心优化2：提取文本，自动跳过空白页
                    text = page.extract_text()
                    if not text or text.strip() == "":
                        logger.info(f"跳过PDF空页：{file_path} 第{page_num}页")
                        continue

                    # 清洗文本
                    text = text.replace("\x00", "").strip()
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": file_path,
                            "category": DOC_CATEGORY_MAP.get(file_name, "other"),
                            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "file_type": "pdf",
                            "page": page_num
                        }
                    )
                    docs.append(doc)

                except Exception as e:
                    # 🔥 核心优化3：跳过损坏页，不崩溃
                    logger.warning(f"跳过PDF损坏页：{file_path} 第{page_num}页")
                    continue

        logger.info(f"✅ 成功加载PDF：{file_path}，有效页数：{len(docs)}")
        return docs

    except Exception as e:
        logger.error(f"PDF文件损坏/无法读取：{file_path}")
        return []

# ===================== 文档加载 =====================
def load_docs_with_metadata():
    """加载多格式文档 + 自动附加元数据"""
    try:
        os.makedirs(DOC_PATH, exist_ok=True)
        logger.info(f"开始加载文档：{os.path.abspath(DOC_PATH)}")
        all_raw_docs = []

        # 定义加载器映射
        loader_mapping = {
            ".txt": (TextLoader, {"encoding": "utf-8"}),
            ".md": (TextLoader, {"encoding": "utf-8"}),
            ".docx": (Docx2txtLoader, {}),
            # PDF单独处理（优化后）
            ".pdf": (load_single_pdf, {})
        }

        # 遍历文档目录
        for root, dirs, files in os.walk(DOC_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file_path)
                file_suffix = os.path.splitext(file_name)[1].lower()

                if file_suffix not in loader_mapping:
                    logger.warning(f"跳过不支持的文件格式：{file_path}")
                    continue

                # 加载文档
                loader_cls, loader_kw = loader_mapping[file_suffix]
                try:
                    if file_suffix == ".pdf":
                        # 调用优化的PDF加载函数
                        docs = loader_cls(file_path)
                    else:
                        loader = loader_cls(file_path, **loader_kw)
                        docs = loader.load()

                    if docs:
                        # 补充元数据
                        for doc in docs:
                            doc.metadata["source"] = file_path
                            doc.metadata["category"] = DOC_CATEGORY_MAP.get(file_name, "other")
                            doc.metadata["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            doc.metadata["file_type"] = file_suffix.lstrip(".")
                        all_raw_docs.extend(docs)
                        logger.info(f"加载 {file_suffix} 文档：{file_name}，共{len(docs)}段")
                except Exception as e:
                    logger.error(f"加载文件失败：{file_path}，错误：{str(e)}")
                    continue

        if not all_raw_docs:
            logger.warning("目录下未找到有效文档")
            return []

        logger.info(f"✅ 所有文档加载完成，总计 {len(all_raw_docs)} 段")
        return all_raw_docs
    except FileNotFoundError as e:
        logger.error(f"文档目录不存在：{str(e)}")
        raise ValueError("文档目录不存在，请检查配置") from e
    except Exception as e:
        logger.error(f"加载文档失败：{str(e)}")
        raise ValueError("加载文档异常") from e

# ===================== 文档分片 =====================
def split_docs(raw_docs):
    """文档分片（保留元数据）"""
    try:
        if not raw_docs:
            logger.warning("待分片文档为空")
            return []
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAY,
            separators=["\n\n", "\n", "。", "；", "！", "？"]
        )
        split_data = splitter.split_documents(raw_docs)
        logger.info(f"✅ 文档分片完成：{len(split_data)} 块")
        return split_data
    except Exception as e:
        logger.error(f"文档分片失败：{str(e)}")
        raise ValueError("文档分片异常") from e

# ===================== 嵌入模型 =====================
def get_embedding():
    """获取嵌入模型"""
    try:
        if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY.strip() == "":
            logger.error("DASHSCOPE_API_KEY 未配置")
            raise ValueError("请配置嵌入模型API Key")
        
        emb = DashScopeEmbeddings(
            dashscope_api_key=DASHSCOPE_API_KEY,
            model=EMBEDDING_MODEL
        )
        logger.info("✅ 嵌入模型初始化成功")
        return emb
    except Exception as e:
        logger.error(f"嵌入模型初始化失败：{str(e)}")
        raise ValueError("嵌入模型初始化异常") from e

# ===================== 向量库基础操作 =====================
def get_vector_db(split_list=None):
    """初始化向量库"""
    try:
        os.makedirs(CHROMA_PATH, exist_ok=True)
        emb = get_embedding()
        logger.info(f"初始化向量库：{CHROMA_PATH}")

        if split_list:
            # 新建向量库（带元数据）
            db = Chroma.from_documents(
                documents=split_list,
                embedding=emb,
                persist_directory=CHROMA_PATH
            )
            db.persist()  # 持久化
            logger.info("✅ 新建向量库成功")
        else:
            # 加载已有向量库
            db = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=emb
            )
            logger.info("✅ 加载已有向量库成功")

        return db
    except Exception as e:
        logger.error(f"向量库初始化失败：{str(e)}")
        raise ValueError("向量库初始化异常") from e

def reset_vector_db():
    """清空全量向量库（优化：确认提示+容错）"""
    try:
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH, ignore_errors=True)
            os.makedirs(CHROMA_PATH, exist_ok=True)
            logger.info("✅ 已清空向量库")
        else:
            logger.info("向量库目录不存在，无需清空")
    except Exception as e:
        logger.error(f"清空向量库失败：{str(e)}")
        raise

# ===================== 向量库增删功能（核心优化） =====================
def add_doc_to_vector_db(file_path):
    """新增单个文档到向量库（支持TXT/PDF/DOCX）"""
    try:
        if not validate_file_path(file_path):
            return False
        
        # 加载单个文档
        file_suffix = os.path.splitext(file_path)[1].lower()
        if file_suffix == ".pdf":
            docs = load_single_pdf(file_path)
        else:
            loader_mapping = {
                ".txt": (TextLoader, {"encoding": "utf-8"}),
                ".md": (TextLoader, {"encoding": "utf-8"}),
                ".docx": (Docx2txtLoader, {})
            }
            if file_suffix not in loader_mapping:
                logger.error(f"不支持的文件格式：{file_suffix}")
                return False
            loader_cls, loader_kw = loader_mapping[file_suffix]
            loader = loader_cls(file_path, **loader_kw)
            docs = loader.load()
            # 补充元数据
            file_name = os.path.basename(file_path)
            for doc in docs:
                doc.metadata["category"] = DOC_CATEGORY_MAP.get(file_name, "other")
                doc.metadata["update_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                doc.metadata["file_type"] = file_suffix.lstrip(".")

        # 分片
        split_data = split_docs(docs)
        if not split_data:
            logger.warning("文档分片后为空，跳过添加")
            return False

        # 添加到向量库
        emb = get_embedding()
        db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=emb
        )
        db.add_documents(split_data)
        db.persist()
        logger.info(f"✅ 成功添加文档到向量库：{file_path}")
        return True
    except Exception as e:
        logger.error(f"添加文档到向量库失败：{file_path}，错误：{str(e)}")
        return False

def delete_doc_from_vector_db(file_name):
    """删除指定文档的向量（按文件名匹配）"""
    try:
        emb = get_embedding()
        db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=emb
        )
        # 按source元数据匹配文件（模糊匹配文件名）
        all_docs = db.get()
        ids_to_delete = []
        for idx, source in enumerate(all_docs["metadatas"]):
            if file_name in source.get("source", ""):
                ids_to_delete.append(all_docs["ids"][idx])
        
        if not ids_to_delete:
            logger.warning(f"未找到匹配的向量：{file_name}")
            return False
        
        # 删除向量
        db.delete(ids=ids_to_delete)
        db.persist()
        logger.info(f"✅ 成功删除 {len(ids_to_delete)} 个向量（匹配文件：{file_name}）")
        return True
    except Exception as e:
        logger.error(f"删除向量失败：{file_name}，错误：{str(e)}")
        return False

# ===================== 分类检索 =====================
def get_retriever_by_category(vector_db, category, top_k=3):
    """按分类标签检索"""
    try:
        retriever = vector_db.as_retriever(
            search_kwargs={
                "k": top_k,
                "filter": {"category": category}
            }
        )
        logger.info(f"👉 启用分类检索：{category}")
        return retriever
    except Exception as e:
        logger.error(f"分类检索器创建失败：{str(e)}")
        raise