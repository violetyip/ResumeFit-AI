import os
import streamlit as st
from dotenv import load_dotenv
from src.llm_extractor import JDExtractor
from src.match import calculate_semantic_enhanced_match, generate_suggestions
from src.pdf_parser import extract_text_from_pdf
from src.semantic import check_missing_skills_semantically

# --- 1. 环境与配置 ---
load_dotenv()
LOCAL_API_KEY = os.getenv("DEEPSEEK_API_KEY")

st.set_page_config(page_title="ResumeFit AI V3.0", page_icon="🎯", layout="wide")

# --- 2. 顶部折叠配置 (废除原有的侧边栏，节省空间) ---
with st.expander("⚙️ 引擎设置 (API Key 配置)", expanded=False):
    user_api_key = st.text_input(
        "输入自定义 API Key (留空则使用默认配置)：",
        type="password"
    )

FINAL_API_KEY = user_api_key if user_api_key else LOCAL_API_KEY

if not FINAL_API_KEY:
    st.error("❌ 请先配置 API Key。")
    st.stop()

extractor = JDExtractor(api_key=FINAL_API_KEY)

# --- 3. 页面主界面 (放大标题字号) ---
st.markdown("<h1 style='text-align: center;'>🎯 ResumeFit AI 智能简历助手</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 18px; margin-bottom: 30px;'>无需手动配置，粘贴即分析。基于 DeepSeek 深度理解全行业岗位需求。</p>",
    unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # 使用 Markdown 的二级标题，比默认的 subheader 更大更醒目
    st.markdown("## 📄 第一步：输入简历")

    # 核心改动：引入 Tabs 标签页，解决上传框和文本框高度不协调的问题
    tab_pdf, tab_text = st.tabs(["📁 上传简历 PDF", "📝 粘贴简历文本"])

    resume_text = ""

    with tab_pdf:
        # 隐藏掉原来那个很小的 label 字体，让界面更清爽
        uploaded_file = st.file_uploader("上传", type=["pdf"], label_visibility="collapsed")
        if uploaded_file is not None:
            resume_text = extract_text_from_pdf(uploaded_file.read())
            st.success("✅ 简历 PDF 读取成功")

    with tab_text:
        pasted_resume_text = st.text_area(
            "文本",
            height=300,
            placeholder="在这里输入你的简历内容...",
            label_visibility="collapsed"
        )
        if pasted_resume_text.strip():
            resume_text = pasted_resume_text

with col2:
    st.markdown("## 💼 第二步：输入目标岗位")
    jd_text = st.text_area(
        "岗位",
        height=360,  # 撑高文本框，使其与左侧 Tabs 整体视觉高度对齐
        placeholder="直接把招聘 App 里的岗位要求复制到这里...\n\n例如：\n1. 负责相关运营工作...\n2. 具备优秀的数据分析能力...",
        label_visibility="collapsed"
    )

st.markdown("---")

# --- 4. 一键诊断逻辑 (核心算法保持原样，未做任何修改) ---
st.markdown("<h2 style='text-align: center;'>🔍 第三步：智能诊断</h2>", unsafe_allow_html=True)
st.write("")  # 增加一点留白

if st.button("🚀 一键生成匹配报告", use_container_width=True, type="primary"):
    if not resume_text.strip() or not jd_text.strip():
        st.warning("⚠️ 简历和岗位描述都要填好才能诊断！")
        st.stop()

    with st.spinner("🧠 正在提取岗位核心要求..."):
        jd_dict = extractor.extract_skills(jd_text)
        if not jd_dict:
            st.error("❌ 岗位解析失败，请检查网络或 Key。")
            st.stop()
        jd_skills = list(jd_dict.keys())

    with st.spinner("🔍 正在扫描简历契合度..."):
        resume_lower = resume_text.lower()
        matched_skills = [s for s in jd_skills if s.lower() in resume_lower]
        missing_skills = [s for s in jd_skills if s not in matched_skills]

        semantic_result = check_missing_skills_semantically(
            resume_text=resume_text,
            missing_skills=missing_skills,
            threshold=0.20
        )

    potential_matches = semantic_result["potential_matches"]
    still_missing_items = semantic_result["still_missing"]
    still_missing_skills = [item["skill"] for item in still_missing_items]

    score_result = calculate_semantic_enhanced_match(
        jd_skills=jd_skills,
        exact_matched_skills=matched_skills,
        potential_matches=potential_matches,
        semantic_weight=0.5
    )

    suggestions = generate_suggestions(still_missing_skills)

    # --- 5. 结果展示 ---
    st.markdown(f"## 🏆 综合匹配度：{score_result['final_score']} / 100")

    res_col1, res_col2, res_col3, res_col4 = st.columns(4)

    with res_col1:
        st.markdown("### 📌 岗位核心要求")
        for s in jd_skills:
            st.write(f"- {s.upper()}")

    with res_col2:
        st.markdown("### ✅ 简历明确写出")
        if matched_skills:
            for s in matched_skills:
                st.success(s.upper())
        else:
            st.write("暂无")

    with res_col3:
        st.markdown("### 🟡 AI 推断具备")
        if potential_matches:
            for item in potential_matches:
                st.warning(f"{item['skill'].upper()} (得分: {item['score']})")
        else:
            st.write("暂无")

    with res_col4:
        st.markdown("### ❌ 核心缺失")
        if still_missing_items:
            for item in still_missing_items:
                st.error(f"{item['skill'].upper()} (得分: {item['score']})")
        else:
            st.success("无缺失")

    # --- 6. 证据溯源 ---
    st.markdown("---")
    st.markdown("### 🧠 判定证据")
    if potential_matches:
        for item in potential_matches:
            with st.expander(f"【{item['skill'].upper()}】判定证据"):
                st.write("**简历原文：**")
                st.write(item['evidence'])
    else:
        st.write("暂无需要溯源的证据。")

    # --- 7. 修改建议 ---
    st.markdown("---")
    st.markdown("### 💡 简历修改建议")
    if suggestions:
        for i, sug in enumerate(suggestions):
            st.info(f"{i + 1}. {sug}")
    else:
        st.success("没有明显需要补充的技能。")