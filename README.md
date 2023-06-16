# Internship_project

## 项目描述

实习期项目主要包含以下三个：
1. 语音识别后的热词识别替换模型： [`hot_words`](./hot_words/README.md)
2. 客服回答质检以及高频问题提取： [`embedding_clustering`](./embedding_clustering/README.md)
3. 对话文本的AI标签： [`labeling`](./labeling/README.md)

## 项目方法

### hot_words
1. 将识别后待纠错文本转化为拼音，eg： 亿量科技-->yi-liang-ke-ji
2. 全局搜索，如果待纠错文本中出现与热词相同拼音的片段，直接替换，eg： 一辆科技-->亿量科技
3. 模糊搜索，基于`fuzzywuzzy`计算热词与待纠错文本片段的拼音字符串的相似度，也即编辑距离
4. 采用`fastapi`部署服务

详见项目代码注释及README

### embedding_clustering
1. 数据构建，获取qa_list
2. sentence embedding，获取向量矩阵
3. 计算标准文档中提供的给定问题与我们在对话中找到的问题之间的相似性
4. 使用GPT API对答案进行评分

此外，我们还做了一些工作来查找“标准问题，也就是高频率问题”：
1. sentence embedding
2. 聚类
3. 对不同的聚类做摘要，提取核心问题
4. TODO：如何回答问题？

详见项目代码注释及README 

### labeling
1. 使用zero-shot classification模型进行AI打标

详见项目代码注释及README

## 项目进展（TODO）

### hot_words
1. 用`SQLite`替换静态文件储存热词
2. 调试更合适的阈值
3. 尝试使用模型的方法做热词替换

### embedding_clustering
1. 提取问题的方式。目前采用的识别方法是关键词定位问题，'？', '？'
2. 聚类的类别数
3. 从各类别抽取问题的方法，目前采用summary
4. 对话质检使用GPT API，稳定性欠佳

### labeling
1. 如何应对高并发，目前服务器的资源有限，并发量难以提升