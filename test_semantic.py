from sentence_transformers import SentenceTransformer, util

model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

print("正在加载模型...")
model = SentenceTransformer(model_name)
print("模型加载完成！")

sentence_a = "使用 Python 对 CSV 数据进行清洗、缺失值处理和统计分析"

sentences_b = [
    "熟悉 Pandas 进行数据处理和数据分析",
    "熟悉 Docker 容器化部署",
    "了解足球比赛战术分析",
    "掌握 SQL 数据库查询和表连接"
]

embedding_a = model.encode(sentence_a, convert_to_tensor=True)
embeddings_b = model.encode(sentences_b, convert_to_tensor=True)

scores = util.cos_sim(embedding_a, embeddings_b)[0]

print("\n原句：")
print(sentence_a)

print("\n相似度结果：")
for sentence, score in zip(sentences_b, scores):
    print(f"{score.item():.4f}  ->  {sentence}")