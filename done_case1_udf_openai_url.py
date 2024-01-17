### 修改api的url？因为cf国内访问可以更快
## 修改openAi的base_url，调用自定义的url
import time
from openai import OpenAI
import openai
import requests

# client = OpenAI()


# 定义 API 密钥和自定义的 base_url
api_key = '123'
custom_base_url = "http://127.0.0.1:5000"

# 创建 OpenAI 客户端实例，并指定自定义的 base_url
client = openai.OpenAI(api_key=api_key, base_url=custom_base_url)

# 使用客户端实例调用 completions.create 方法
resp = client.chat.completions.create(
    model="WENXIN",
    messages=[
        {"role": "user", "content": "你好，你是谁？"},
    ]
)

# 打印响应
print(f'resp={resp}')
