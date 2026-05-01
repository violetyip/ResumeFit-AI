# ResumeFit AI: 语义增强型简历匹配引擎

> **拒绝 LLM 套壳**。基于白盒规则与向量空间模型 (VSM) 的可解释性分析系统。

## 🌟 项目亮点
*   **不仅仅是关键词**：引入 `sentence-transformers` 提取语义特征，识别简历中的隐式技能表达。
*   **白盒打分机制**：将匹配度拆解为“精确命中”与“语义潜力”，计算逻辑透明可查。
*   **PDF 智能解析**：利用 `PyMuPDF` 实现非结构化文档到结构化文本的精准转换。

## 🧪 算法核心
系统通过余弦相似度（Cosine Similarity）计算简历文本向量 $\mathbf{A}$ 与预设技能画像向量 $\mathbf{B}$ 的匹配程度，从而挖掘出未直接写明但语义相关的能力：
$$similarity = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$

## 🛠️ 快速开始
1. 安装依赖：`pip install -r requirements.txt`
2. 启动程序：`streamlit run app.py`