import jieba
import re

# 我们 V1 版本的“核心技术词典”，你可以随时往里加词，都用小写
TECH_DICT = [
    "python", "java", "c++", "go", "sql", "git", "linux", "docker",
    "mysql", "redis", "mongodb", "spring", "flask", "fastapi",
    "pandas", "numpy", "scikit-learn", "matplotlib",
    "pytorch", "tensorflow", "nlp", "cv", "机器学习", "深度学习",
    "大模型", "llm", "rag", "langchain", "prompt", "transformer"
]


def clean_text(text):
    """文本预处理：转小写，去标点"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return text


def extract_skills(text):
    """核心提取逻辑：结巴分词 + 暴力兜底匹配"""
    if not text:
        return []

    cleaned_text = clean_text(text)
    words = jieba.lcut(cleaned_text)
    found_skills = set()

    # 精准词汇匹配
    for word in words:
        if word in TECH_DICT:
            found_skills.add(word)

    # 子串暴力防漏匹配
    for tech in TECH_DICT:
        if tech in cleaned_text:
            found_skills.add(tech)

    return sorted(list(found_skills))