import streamlit as st
from src.extract import extract_skills
from src.match import calculate_match, calculate_semantic_enhanced_match, generate_suggestions
from src.pdf_parser import extract_text_from_pdf
from src.semantic import check_missing_skills_semantically

st.set_page_config(page_title="ResumeFit AI", page_icon="🎯", layout="wide")

st.title("🎯 ResumeFit AI")
st.markdown("**面向大学生的简历-岗位匹配分析与优化系统 (V2.0 语义增强版)**")
st.markdown("---")

col1, col2 = st.columns(2)

# --- 左列：支持 PDF 上传 + 文本粘贴 ---
with col1:
    st.subheader("📄 第一步：输入简历")

    uploaded_file = st.file_uploader("方式一：上传你的简历 PDF", type=["pdf"])

    pasted_resume_text = st.text_area(
        "方式二：直接粘贴简历文本（推荐开发测试时使用）",
        height=220,
        placeholder="例如：本人熟悉 Python，完成过学生成绩预测项目。项目中负责 CSV 数据清洗、缺失值处理、特征工程和统计分析。熟悉 Git 版本管理。"
    )

    resume_text = ""

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        resume_text = extract_text_from_pdf(file_bytes)

        st.success("✅ PDF 解析成功！后台已获取简历内容。")
        with st.expander("点击查看 PDF 提取出的纯文本"):
            st.write(resume_text)

    if pasted_resume_text.strip():
        resume_text = pasted_resume_text
        st.info("当前使用的是手动粘贴的简历文本。")

# --- 右列：岗位输入 ---
with col2:
    st.subheader("💼 第二步：输入目标岗位 (JD)")
    jd_text = st.text_area(
        "请在此粘贴目标岗位描述：",
        height=200,
        placeholder="例如：要求熟练掌握 Python、SQL，了解 NLP 和大模型相关框架..."
    )

st.markdown("---")

# --- 核心分析逻辑 ---
if st.button("🚀 开始深度匹配分析", type="primary"):
    if resume_text.strip() and jd_text.strip():
        # 1. 关键词匹配
        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        score, matched_skills, missing_skills = calculate_match(resume_skills, jd_skills)

        # 2. 语义补查：只检查关键词系统认为“缺失”的技能
        with st.spinner("正在进行语义补查，请稍等..."):
            semantic_result = check_missing_skills_semantically(
                resume_text=resume_text,
                missing_skills=missing_skills,
                threshold=0.40
            )

        potential_matches = semantic_result["potential_matches"]
        still_missing_items = semantic_result["still_missing"]
        still_missing_skills = [item["skill"] for item in still_missing_items]

        # 3. 语义增强评分
        score_result = calculate_semantic_enhanced_match(
            jd_skills=jd_skills,
            exact_matched_skills=matched_skills,
            potential_matches=potential_matches,
            semantic_weight=0.6
        )

        # 4. 建议生成：只针对“语义上仍然缺失”的技能给建议
        suggestions = generate_suggestions(still_missing_skills)
        # --- 结果展示 ---
        st.subheader(f"📊 语义增强匹配度：{score_result['final_score']}/100")

        st.caption(
            f"关键词精确匹配：{score_result['exact_score']}/100 ｜ "
            f"语义补充分：+{score_result['semantic_bonus']} ｜ "
            f"命中情况：精确 {score_result['exact_hit_count']} 个，"
            f"语义潜在匹配 {score_result['semantic_hit_count']} 个，"
            f"岗位共要求 {score_result['total_required_count']} 个技能"
        )

        res_col1, res_col2, res_col3, res_col4 = st.columns(4)

        with res_col1:
            st.markdown("**📌 岗位核心要求**")
            if jd_skills:
                for s in jd_skills:
                    st.write(f"- {s.upper()}")
            else:
                st.write("暂无识别结果")

        with res_col2:
            st.markdown("**✅ 精确匹配技能**")
            if matched_skills:
                for s in matched_skills:
                    st.success(s.upper())
            else:
                st.write("暂无精确匹配技能")

        with res_col3:
            st.markdown("**🟡 语义潜在匹配**")
            if potential_matches:
                for item in potential_matches:
                    st.warning(f"{item['skill'].upper()}  相似度：{item['score']}")
            else:
                st.write("暂无语义潜在匹配")

        with res_col4:
            st.markdown("**❌ 仍需补充技能**")
            if still_missing_items:
                for item in still_missing_items:
                    st.error(f"{item['skill'].upper()}  相似度：{item['score']}")
            else:
                st.success("暂无明显缺失技能")

        # --- 语义证据展示 ---
        st.markdown("---")
        st.markdown("### 🧠 语义补查证据")

        if potential_matches:
            st.markdown("这些技能虽然没有被关键词系统精确命中，但简历中存在相关表达：")

            for item in potential_matches:
                with st.expander(f"{item['skill'].upper()} ｜ 相似度：{item['score']}"):
                    st.write("**证据句：**")
                    st.write(item["evidence"])
                    st.info(
                        "解释：该技能没有被简历直接写出，但语义模型认为简历中的这句话与该技能存在相关性。"
                    )
        else:
            st.write("暂无语义补查命中的潜在技能。")

        # --- 优化建议 ---
        st.markdown("### 💡 智能优化建议")

        if suggestions:
            for i, sug in enumerate(suggestions):
                st.info(f"{i + 1}. {sug}")
        else:
            st.success("当前没有明显需要补充的技能，建议继续优化项目描述和量化结果。")

    else:
        st.warning("⚠️ 请确保已上传简历，并填写了右侧的岗位描述！")