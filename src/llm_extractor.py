# src/llm_extractor.py
import json
from openai import OpenAI


class JDExtractor:
    def __init__(self, api_key: str):
        # 初始化大模型客户端。DeepSeek 完美兼容 OpenAI 的接口格式
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def extract_skills(self, jd_text: str) -> dict:
        """
        核心方法：将非结构化的 JD 文本，转化为结构化的技能语义画像 JSON
        """
        system_prompt = """
        你是一个资深的 AI 架构师和技术 HR。
        你的任务是阅读给定的招聘岗位描述（JD），提取出其中的硬性专业技能要求，并为每个技能生成一段用于“向量语义检索”的扩展描述。

        【扩展描述要求】
        不要写长句，用空格分隔的关键词组成，涵盖该技能的具体应用场景、细分技术点或相关工具。

        【输出格式严格要求】
        必须只输出合法的纯 JSON 对象，绝对不要包含任何 Markdown 标记（如 ```json ），绝对不要有任何前言或解释说明。
        示例格式：
        {
            "Python": "Python编程 脚本开发 数据处理 自动化开发",
            "深度学习": "CNN RNN Transformer 模型微调 PyTorch",
            "新媒体运营": "图文排版 用户增长 数据复盘 爆款标题 小红书"
        }
        """

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请解析以下 JD：\n{jd_text}"}
                ],
                temperature=0.1,  # 极低的温度，消除大模型的“幻觉”，保证每次输出格式极其稳定
                max_tokens=1000
            )

            raw_output = response.choices[0].message.content.strip()

            # 容错清洗：防止大模型偶尔犯病加上 markdown 标记
            if raw_output.startswith("```json"):
                raw_output = raw_output[7:-3].strip()
            elif raw_output.startswith("```"):
                raw_output = raw_output[3:-3].strip()

            # 将字符串解析为 Python 字典
            parsed_dict = json.loads(raw_output)
            return parsed_dict

        except json.JSONDecodeError:
            print("❌ 大模型返回的格式无法解析为 JSON，请检查输出。")
            return {}
        except Exception as e:
            print(f"❌ API 调用失败: {e}")
            return {}