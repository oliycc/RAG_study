# Python 中的结构化提取，由 llms 提供支持，旨在实现简单性、透明度和可控性。输出的格式化依赖于模型实现
# 解决ymetaphore隐喻问题提高查询的精确率和召回率；实现数据结构化
# https://jxnl.github.io/instructor/api/
# Explain
# 1. 根据openAI工具使用范式，结构化工具为josn范式
# 2. 隐语问题 todo

import instructor
from openai import OpenAI
from pydantic import BaseModel

# This enables response_model keyword
# from client.chat.completions.create

### 修改api的url？因为cf国内访问可以更快


# 使用llm进行内容结构化提取
# 定义 API 密钥和自定义的 base_url
api_key = '123'
custom_base_url = "http://127.0.0.1:5000"

# 创建 OpenAI 客户端实例，并指定自定义的 base_url
customOpenAi = OpenAI(api_key=api_key, base_url=custom_base_url)
client = instructor.patch(customOpenAi)

class UserDetail(BaseModel):
    name: str
    age: int

# 调用大模型的请求参数：{'messages': [{'role': 'user', 'content': '提取信息 Jason今年25岁'}], 'model': 'WENXIN', 'function_call': {'name': 'UserDetail'}, 'functions': [{'name': 'UserDetail', 'description': 'Correctly extracted `UserDetail` with all the required parameters with correct types', 'parameters': {'properties': {'name': {'title': 'Name', 'type': 'string'}, 'age': {'title': 'Age', 'type': 'integer'}}, 'required': ['age', 'name'], 'type': 'object'}}], 'max_tokens': 10000000}
# openAi的参数说明 https://platform.openai.com/docs/introduction
# 解读:https://zhuanlan.zhihu.com/p/637002733
# openAI微调了模型实现了“可识别且格式化输出”
user = client.chat.completions.create(
    model="gpt-3.5",  # 可以使用本地的llm
    response_model=UserDetail,
    messages=[
        {"role": "user", "content": "提取信息 Jason今年25岁"},
    ]
)

assert isinstance(user, UserDetail)
assert user.name == "Jason"
assert user.age == 25
print(f'finish!!!')