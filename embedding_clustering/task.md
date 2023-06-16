### 5.6
* 1、先从客户问题入手，只关注客户的问题
* 2、对客户的问题聚类，看聚类效果好不好。看起来`Ward Hierarchical`还不错，对比一下`Bertopic`
```python
sentence_model = pipeline("feature-extraction", model="GanymedeNil/text2vec-large-chinese")
topic_model = BERTopic(embedding_model=sentence_model).fit(docs)
```
* 3、找到客户问的最多的`top 20`的问题
* 4、这`top20`的问题，每一个问题，不同的销售都是怎么回复的，把相应的回复提取出来
* 5、在标准话术文档（`https://wangjizhe.notion.site/733d96766d92433a88fd2cbb8fe2f148`）里，找到对应的`QA`，将电话中的销售回复和标准话术`QA`做对比（让`ChatGPT`进行打分，指出销售实际回复与标准话术的不足之处）


### 5.17
* 1、聚类，需确定聚类数`cluster_num`，以及用于做最后问题识别和审核的问题数`k`
* 2、筛选回答的客服回答数`response_num`，暂定为`20`
* 3、编成合适的脚本


### 5.18
* 1、如何确定问题？目前为基于规则：使用问号对语音识别中的客户发言进行问题的确定提取。
    * 寻找问句数据集
    * 构建高校模型
* 2、如何确定最佳聚类数：目前为肉眼观察
    * 更换sentence embedding预训练模型
* 3、总结问题，作为`QA data`的一部分