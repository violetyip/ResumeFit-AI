# src/match.py
import os
from typing import List, Dict
from openai import OpenAI


def calculate_semantic_enhanced_match(
        jd_skills: List[str],
        exact_matched_skills: List[str],
        potential_matches: List[Dict],
        semantic_weight: float = 0.5
) -> Dict:
    """
    计算语义增强后的匹配得分。
    (这段逻辑保持不变，确保评分系统稳定)
    """
    total_required = len(jd_skills)
    if total_required == 0:
        return {
            "final_score": 0,
            "exact_score": 0,
            "semantic_bonus": 0,
            "exact_hit_count": 0,
            "semantic_hit_count": 0,
            "total_required_count": 0
        }

    exact_hit_count = len(exact_matched_skills)
    semantic_hit_count = len(potential_matches)

    # 基础分：精确匹配
    exact_score = (exact_hit_count / total_required) * 100

    # 奖励分：语义匹配 (给予一定折扣)
    semantic_bonus = (semantic_hit_count / total_required) * 100 * semantic_weight

    final_score = round(min(exact_score + semantic_bonus, 100), 1)

    return {
        "final_score": final_score,
        "exact_score": round(exact_score, 1),
        "semantic_bonus": round(semantic_bonus, 1),
        "exact_hit_count": exact_hit_count,
        "semantic_hit_count": semantic_hit_count,
        "total_required_count": total_required
    }


def generate_suggestions(missing_skills: List[str]) -> List[str]:
    """
    核心升级：调用 DeepSeek 生成定制化的简历优化建议。
    不再是硬邦邦的“建议补充经验”，而是具体的“怎么写”。
    """
    if not missing_skills:
        return ["你的简历已经非常完美，与岗位高度匹配！建议重点突出项目中的量化成果。"]

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return [f"建议针对缺失技能 {s} 补充相关项目经验。" for s in missing_skills]

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # 将缺失技能列表转为字符串
    skills_str = "、".join(missing_skills)

    prompt = f"""
    你是一个资深的职业规划导师。候选人目前正在投递一个岗位，但在以下技能上存在缺失：【{skills_str}】。

    请根据这些缺失技能，为候选人提供 3-4 条极具实操性的简历修改建议。

    要求：
    1. 语气专业且鼓励，不要只说“去学习”，要教他如何在简历中“体现潜力”。
    2. 如果是数据库、编程语言等，建议他如何在现有项目中寻找关联点进行包装。
    3. 每条建议要简短有力（不超过 60 字）。
    4. 采用“👉 建议：...”的格式输出。
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # 增加一点创造力，让建议更丰富
            max_tokens=500
        )
        # 将生成的文本按行拆分成列表
        suggestion_text = response.choices[0].message.content.strip()
        suggestions = [s.strip() for s in suggestion_text.split('\n') if s.strip()]
        return suggestions
    except Exception as e:
        print(f"建议引擎故障: {e}")
        return [f"👉 针对 {s}，建议在简历中补充具体的应用场景或学习成果描述。" for s in missing_skills]