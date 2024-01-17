本着开发具有强鲁棒性的”基于大模型的工具使用框架“的目的，开始从0开始系统性学习RAG（retrive-augmented genration）技术
这个项目按照本人学习过程，系统整理了“实操案例”（case），旨在帮助初学者快速学会使用RAG现有的技术栈（langChain为例），工具框架（BMTools）
结合实际工程和场景，给出了“操作数据库”，“调用api”，“查询文档"的实操案例
⭐️⭐️⭐️ 本项目包含了文献、由浅到深的实操case、自定义openAi的接口模版
⭐️⭐️⭐️ 教程特点:case导向，文档辅助，精简主义
⭐️⭐️⭐️ 针对BMTool中存在的：
1） 问题1：国内无法调用openAI接口：解决方案：util中增加了自定义llm调用接口实现和OpenAI客户端无缝衔接
2） （TODO）问题2：BM使用了Azure OpenAI Embedding接口，是个付费接口，穷孩子没付费。解决方案：util中增加OpenAIEmbeddings兼容的自定义embedding接口
改进后的项目BMTools_plus: https://github.com/oliycc/BMTools_plus （这个项目会根据常见工程需求不断更新）
# 注意：当前case增在编码，本教程进行中，非完整版。。。。
# 学习目标
 1）清楚RAG系统的核心构成并能够熟练使用langchain技术栈 （外部api、db、文档）
 2）了解熟悉工具的范式和标准结构
 3）了解并能够使用BMTools工具框架
# 适用人群
熟悉python语言
会使用vscode编码器
对大模型llm的能力有了解
对提示工程(Prompt Engineering)概念有了解，清楚COT思维链和reAct框架（不了解可以先看相关论文）
想要系统性学习RAG，并快速掌握RAG技术栈

# 学习顺序
1. 先阅读paper_list文章
2. 依次学习case（涉及预热知识的会引导）
# 学习目录
TODO (当前学习整理中....)
1. 。。。。。

# 关于学习方法论
难点：知识多而杂，二手知识准确信未知，学习的深度难以确定，学习节奏和内容难以安排
能力: 信息检索能力（如何找全最近相关文献？如何找到最近相关github项目？主流产品的采取的方案？）、源码解读、系统性汇总

不要轻易放过不懂的词汇，不然可能忽略有用信息

思考:对上面说的”能力“又是否能够通过llm工具框架得以解决呢，给llm”文献查询“能力

# 联系作者
一个人也许能走得很快，但一群人肯定走得更远
如果也对RAG和LLM方向感兴趣，或者对本教程有疑问，又或者在RAG落地遇到问题...欢迎小伙伴来扰
oliycc.llh@gmail.com 



