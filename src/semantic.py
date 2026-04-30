import re
from functools import lru_cache
from typing import List, Dict

from sentence_transformers import SentenceTransformer, util


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


SKILL_PROFILES = {
    "Python": "Python 编程 脚本开发 数据处理 自动化开发",
    "SQL": "SQL 数据库查询 MySQL 关系型数据库 数据表 SELECT JOIN GROUP BY 表连接",
    "Pandas": "Pandas DataFrame CSV Excel 表格数据处理 数据清洗 数据分析",
    "NumPy": "NumPy 数组 矩阵 数值计算 科学计算",
    "Scikit-learn": "Scikit-learn sklearn 机器学习 分类 回归 聚类 模型训练 模型评估",
    "PyTorch": "PyTorch 深度学习 神经网络 模型训练 张量",
    "TensorFlow": "TensorFlow 深度学习 神经网络 模型训练",
    "Machine Learning": "机器学习 特征工程 模型训练 模型评估 分类 回归 预测",
    "Deep Learning": "深度学习 神经网络 CNN RNN Transformer 模型训练",
    "NLP": "自然语言处理 文本分析 分词 语义匹配 文本分类 信息抽取",
    "Computer Vision": "计算机视觉 图像识别 目标检测 图像分类 OpenCV YOLO",
    "LLM": "大语言模型 生成式AI Prompt 大模型应用 文本生成",
    "RAG": "RAG 检索增强生成 向量数据库 知识库问答 文档问答 语义检索",
    "LangChain": "LangChain 大模型应用开发 RAG Agent Chain 工作流",
    "Docker": "Docker 容器化 镜像 部署 环境隔离 服务部署",
    "Git": "Git 版本控制 GitHub 分支 Pull Request 代码协作",
    "Linux": "Linux 命令行 Shell 服务器 环境配置",
    "FastAPI": "FastAPI Python 后端 API 接口 Web服务",
    "Flask": "Flask Python 后端 Web框架 API接口",
    "Streamlit": "Streamlit 数据应用 可视化 Demo Web界面",
    "MySQL": "MySQL 关系型数据库 SQL 数据表 查询",
    "Redis": "Redis 缓存 键值数据库 高性能存储",
    "MongoDB": "MongoDB NoSQL 文档数据库",
    "HTML": "HTML 前端 页面结构",
    "CSS": "CSS 前端 样式 页面布局",
    "JavaScript": "JavaScript 前端 交互 浏览器 Web开发",
}


def get_skill_profile(skill: str) -> str:
    """
    根据技能名获取语义画像，支持大小写不敏感匹配。
    例如 pandas / Pandas / PANDAS 都能匹配到 Pandas 的语义画像。
    """
    skill_clean = skill.strip()

    for profile_key, profile_text in SKILL_PROFILES.items():
        if profile_key.lower() == skill_clean.lower():
            return profile_text

    return skill_clean


@lru_cache(maxsize=1)
def load_model():
    """
    加载语义向量模型。
    使用缓存，避免每次调用都重新加载模型。
    """
    return SentenceTransformer(MODEL_NAME)


def split_sentences(text: str) -> List[str]:
    """
    将长文本切分成句子，方便后续找语义匹配证据。
    """
    if not text:
        return []

    text = text.replace("\r", "\n")
    parts = re.split(r"[。！？!?；;\n]+", text)

    sentences = []
    for part in parts:
        sentence = re.sub(r"\s+", " ", part).strip()
        if len(sentence) >= 4:
            sentences.append(sentence)

    return sentences


def calculate_similarity(sentence_a: str, sentence_b: str) -> float:
    """
    计算两个句子的语义相似度。
    返回 0-1 之间的小数，越高表示越相似。
    """
    model = load_model()

    embedding_a = model.encode(sentence_a, convert_to_tensor=True)
    embedding_b = model.encode(sentence_b, convert_to_tensor=True)

    score = util.cos_sim(embedding_a, embedding_b).item()

    return round(score, 4)


def find_best_matching_sentence(query: str, candidate_sentences: List[str]) -> Dict:
    """
    给定一个查询句子，在候选句子中找到最相似的一句。

    例如：
    query = "熟悉 Pandas 进行数据处理"
    candidates = 简历里的所有句子
    """
    if not candidate_sentences:
        return {
            "query": query,
            "best_sentence": "",
            "score": 0.0
        }

    model = load_model()

    query_embedding = model.encode(query, convert_to_tensor=True)
    candidate_embeddings = model.encode(candidate_sentences, convert_to_tensor=True)

    scores = util.cos_sim(query_embedding, candidate_embeddings)[0]

    best_index = int(scores.argmax())
    best_score = scores[best_index].item()

    return {
        "query": query,
        "best_sentence": candidate_sentences[best_index],
        "score": round(best_score, 4)
    }


def check_missing_skills_semantically(
    resume_text: str,
    missing_skills: List[str],
    threshold: float = 0.40
) -> Dict:
    """
    对关键词匹配中判断为“缺失”的技能进行语义补查。

    返回两类结果：
    1. potential_matches: 简历中可能已经隐式体现的技能
    2. still_missing: 语义上也没有明显体现的技能
    """
    resume_sentences = split_sentences(resume_text)

    potential_matches = []
    still_missing = []

    if not resume_sentences:
        return {
            "potential_matches": potential_matches,
            "still_missing": [
                {
                    "skill": skill,
                    "score": 0.0,
                    "evidence": ""
                }
                for skill in missing_skills
            ]
        }

    for skill in missing_skills:
        query = get_skill_profile(skill)

        result = find_best_matching_sentence(
            query=query,
            candidate_sentences=resume_sentences
        )

        item = {
            "skill": skill,
            "score": result["score"],
            "evidence": result["best_sentence"]
        }

        if result["score"] >= threshold:
            potential_matches.append(item)
        else:
            still_missing.append(item)

    return {
        "potential_matches": potential_matches,
        "still_missing": still_missing
    }


if __name__ == "__main__":
    resume_text = """
    本人熟悉 Python，完成过学生成绩预测项目。
    项目中负责 CSV 数据清洗、缺失值处理、特征工程和统计分析。
    熟悉 Git 版本管理。
    """

    missing_skills = [
        "pandas",
        "sql",
        "docker",
        "machine learning"
    ]

    result = check_missing_skills_semantically(
        resume_text=resume_text,
        missing_skills=missing_skills,
        threshold=0.40
    )

    print("可能已经隐式体现的技能：")
    for item in result["potential_matches"]:
        print(f"- {item['skill']} | 相似度：{item['score']} | 证据句：{item['evidence']}")

    print("\n仍然缺失的技能：")
    for item in result["still_missing"]:
        print(f"- {item['skill']} | 相似度：{item['score']} | 最接近句子：{item['evidence']}")