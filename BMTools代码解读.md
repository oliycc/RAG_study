解读开源项目BMTool源码
回答：
1）如何判断是否需要使用工具
2）生态工具上百个，"如何挑选出相关的工具"
3）如何组织工具之间并行，串行关系; 动态推理决策
# 先让项目run起来
先熟悉怎么使用，才能聊如何实现


# 剖析-场景：调用已有工具
## 流程：
用户提问 → API如果搞的定，则直接回答 → 用户收到
用户提问 → API如果搞不定，则向“外援”求助 → Function Calling回答 → OpenAI API收到然后润色 → 用户收到

# 架构
整个项目分为：工具管理服务端+llm控制器

## 工具信息标准化
工具信息
{
    "schema_version": "v1",
    "name_for_human": name_for_human,
    "name_for_model": name_for_model,
    "description_for_human": description_for_human,
    "description_for_model": description_for_model,
    "auth": {
        "type": "none",
    },
    "api": {
        "type": "openapi",
        "url": "/openapi.json",
        "is_user_authenticated": False,
    },
    "author_github": author_github,
    "logo_url": logo_url,
    "contact_email": contact_email,
    "legal_info_url": legal_info_url,
}

## swagger生成的符合openAPI的restful 工具接口


## 工具管理&&检索环节

OpenAIEmbeddings 选择text-embedding-ada-002模型  
存入向量库的是：api_info["name_for_model"] + ". " + api_info["description_for_model"]
文档映射dict
    self.documents[tool_name] = {
        "document": document,
        "embedding": document_embedding[0]
    }

运行host_local_tools.py就会加载所有工具

embbeding服务选择了langchain中embedding，默认是Azure OpenAI 生成嵌入（需要付费的）
note：可以提供OpenAIEmbeddings客户端兼容的自定义Embedding


## llm控制器



# 评测工平台
https://github.com/OpenBMB/BMTools/blob/main/README_zh.md
