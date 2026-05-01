# src/semantic.py
import os
from typing import List, Dict
from openai import OpenAI

def check_missing_skills_semantically(
    resume_text: str,
    missing_skills: List[str],
    threshold: float = 0.0 # 废弃本地门槛
) -> Dict:
    """
    V3.0 终极版语义补查：
    开除本地小模型，直接让 DeepSeek 阅读完整简历寻找隐性证据。
    精准解决“U-Net”无法匹配“分割模型”的行业概念壁垒。
    """
    potential_matches = []
    still_missing = []

    if not resume_text or not missing_skills:
        return {
            "potential_matches": [],
            "still_missing": [{"skill": s, "score": 0.0, "evidence": ""} for s in missing_skills]
        }

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {
            "potential_matches": [],
            "still_missing": [{"skill": s, "score": 0.0, "evidence": ""} for s in missing_skills]
        }

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    for skill in missing_skills:
        prompt = f"""
        你是一个善于挖掘人才潜力的资深技术面试官。
        请仔细阅读以下候选人的完整简历全文，判断简历中是否能体现出他具备学习、理解或掌握【{skill}】的经验或潜力。

        【核心判断规则】：
        1. 必须具备极强的技术概念映射能力！例如：看到 U-Net 就要知道这是分割模型；看到 MySQL 就要算作数据库。
        2. 只要简历中提到了相关的具体工具、主修课程、算法名字、或可迁移的项目经验，都算作具备潜力。
        3. 如果具备，请务必回复 "YES|提取最能证明这一点的简历原话" (例如：YES|熟悉 CNN、U-Net 等模型)
        4. 如果全文阅读后发现完全不沾边，请仅回复 "NO"

        【候选人简历全文】：
        {resume_text}

        请严格按照 "YES|证据" 或 "NO" 的格式输出，绝对不要有任何多余的解释。
        """

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, # 保持严谨客观
                max_tokens=60
            )
            result_text = response.choices[0].message.content.strip()

            if result_text.startswith("YES"):
                # 解析出 AI 找到的证据句
                parts = result_text.split("|", 1)
                evidence = parts[1] if len(parts) > 1 else "基于全文上下文推断具备相关基础。"
                potential_matches.append({
                    "skill": skill,
                    "score": 0.85, # 既然大模型判定认可，直接给高分奖励
                    "evidence": evidence
                })
            else:
                still_missing.append({
                    "skill": skill,
                    "score": 0.0,
                    "evidence": ""
                })
        except Exception as e:
            print(f"DeepSeek 全文分析失败: {e}")
            still_missing.append({"skill": skill, "score": 0.0, "evidence": ""})

    return {
        "potential_matches": potential_matches,
        "still_missing": still_missing
    }