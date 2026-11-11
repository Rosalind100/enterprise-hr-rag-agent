import streamlit as st
import requests
import re
import html

# ==================== 页面配置 ====================
st.set_page_config(page_title="HR 智能回复助手", page_icon="💼", layout="wide", initial_sidebar_state="collapsed")

BACKEND_URL = "http://127.0.0.1:8000/chat"

# ==================== 全局 CSS ====================
st.markdown("""
<style>
    /* 隐藏默认元素 */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* 全局背景 */
    html, body, .stApp {
        background-color: #F4F8F7 !important;
        font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }
    
    /* 顶部深青色导航栏 */
    .app-header {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 100;
        background: #0E4B51 !important; 
        color: #FFFFFF;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 10px rgba(14, 75, 81, 0.2);
    }
    .app-title { font-size: 18px; font-weight: 600; color: #FFFFFF; margin: 0; }
    .app-subtitle { font-size: 12px; color: #A2C9C5; margin-top: 4px; }

    /* 聊天气泡样式 */
    .bubble-row { display: flex; margin-bottom: 20px; }
    .bubble-row.user { justify-content: flex-end; }
    .bubble {
        max-width: 80%;
        padding: 12px 16px;
        border-radius: 16px;
        font-size: 15px;
        line-height: 1.6;
    }
    .bubble-user {
        background: linear-gradient(135deg, #12B0A0 0%, #0E8C7F 100%) !important;
        color: #FFFFFF;
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 12px rgba(18, 176, 160, 0.2);
    }
    .bubble-ai {
        background: #FFFFFF !important;
        color: #333333;
        border-radius: 16px;
        border-bottom-left-radius: 4px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        border: 1px solid #E2ECEA;
    }
    .source-line { font-size: 12px; color: #888; margin: -12px 0 20px 8px; }

    /* 右侧数据看板卡片 */
    .stat-card {
        background: linear-gradient(135deg, #12B0A0 0%, #0E8C7F 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(18, 176, 160, 0.2);
    }
    .stat-card-white {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        border: 1px solid #E2ECEA;
    }
    .stat-num { font-size: 36px; font-weight: 700; margin: 8px 0; }
    .stat-label { font-size: 14px; opacity: 0.9; }
    
    /* 空状态 */
    .empty-state { text-align: center; padding: 100px 20px; color: #AAA; }
    .empty-state-icon { font-size: 48px; margin-bottom: 16px; color: #C8CDD3; }
</style>
""", unsafe_allow_html=True)

# ==================== 工具函数：清洗 Markdown ====================
def clean_markdown(text):
    """将 Markdown 转换为可在 HTML 气泡中渲染的安全文本"""
    if not text:
        return ""
    safe = html.escape(text)
    # 加粗处理
    safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
    # 清除多余星号
    safe = safe.replace("* ", "").replace("*", "")
    # 换行处理
    safe = safe.replace("\n", "<br>")
    return safe

# ==================== 状态初始化 ====================
if "messages" not in st.session_state: st.session_state.messages = []
if "total_queries" not in st.session_state: st.session_state.total_queries = 0
if "faq_count" not in st.session_state: st.session_state.faq_count = 0
if "rag_count" not in st.session_state: st.session_state.rag_count = 0

# ==================== 顶部导航 ====================
st.markdown("""
<div class="app-header">
  <div>
    <div class="app-title">💼 HR 智能回复助手</div>
    <div class="app-subtitle">自动识别咨询类型 · 智能生成回复</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="margin-top: 60px;"></div>', unsafe_allow_html=True)

# ==================== 左右分栏布局 ====================
col_chat, col_stats = st.columns([0.65, 0.35])

# ---------- 左侧：聊天区 ----------
with col_chat:
    chat_box = st.container(height=600, border=False)
    with chat_box:
        if not st.session_state.messages:
            st.markdown("""
            <div class="empty-state">
              <div class="empty-state-icon">💬</div>
              <div class="empty-state-title">开始你的第一个咨询</div>
              <div class="empty-state-desc">支持入职、考勤、请假、差旅报销等制度问答。</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for m in st.session_state.messages:
                if m["role"] == "user":
                    st.markdown(f'<div class="bubble-row user"><div class="bubble bubble-user">{m["content"]}</div></div>', unsafe_allow_html=True)
                else:
                    clean_content = clean_markdown(m["content"])
                    st.markdown(f'<div class="bubble-row"><div class="bubble bubble-ai">{clean_content}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="source-line">数据来源：{m.get("source", "UNKNOWN")}</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("请输入问题", placeholder="例如：入职材料 | 报销标准 | 年假怎么休？", label_visibility="collapsed")
        submitted = st.form_submit_button("发送", use_container_width=True)

# ---------- 右侧：数据看板 ----------
with col_stats:
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">累计咨询次数</div>
        <div class="stat-num">{st.session_state.total_queries}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-card-white">
        <div class="stat-label" style="color: #666;">FAQ 极速命中</div>
        <div class="stat-num" style="color: #0E4B51;">{st.session_state.faq_count}</div>
        <hr style="margin: 15px 0; border: 0; border-top: 1px dashed #E2ECEA;">
        <div class="stat-label" style="color: #666;">RAG 深度检索</div>
        <div class="stat-num" style="color: #12B0A0;">{st.session_state.rag_count}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("清空对话记录", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_queries = 0
        st.session_state.faq_count = 0
        st.session_state.rag_count = 0
        st.rerun()

# ==================== 提交处理逻辑 ====================
if submitted and user_input.strip():
    query = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.total_queries += 1

    history = ""
    for m in st.session_state.messages[:-1]:
        prefix = "用户：" if m["role"] == "user" else "助手："
        history += f"{prefix}{m['content']}\n"

    with st.spinner("正在思考..."):
        try:
            resp = requests.post(BACKEND_URL, json={"query": query, "history": history}, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("answer", "（后台未返回有效回答）")
            source = data.get("source", "UNKNOWN").upper()
            
            if source == "FAQ": st.session_state.faq_count += 1
            elif source == "RAG": st.session_state.rag_count += 1
                
            st.session_state.messages.append({"role": "assistant", "content": answer, "source": source})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ 请求异常：{e}", "source": "ERROR"})
            
    st.rerun()