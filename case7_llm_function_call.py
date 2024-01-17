
# openAI的function_calling功能通过微调模型得到的，这个是基于prompt的平替
# 能够提供给llm使用的工具 需要具有一定规范，其描述和名字非常重要


# openAi的参数说明 https://platform.openai.com/docs/introduction
# 解读:https://zhuanlan.zhihu.com/p/637002733


# 使用langchian 实现  https://zhuanlan.zhihu.com/p/641239259

# 场景：帮我给小美发一封邮件，告诉她我晚上不回去吃了
# 第一次llm工具决策
# 1. 决策使用到的工具链
# 2. 每个工具的入参
# 第二次llm总结信息
# 3. 根据工具返回结果，返回最后结论
# 返回结果
{'id': 5000469, 'object': 'text_completion', 'created': 1705395400, 'model': 'WENXIN', 'choices': [{'message': {'role': 'user', 'content': '从您提供的信息中可以提取出如下涉及Jason年龄的信息：\n- Jason：\n\t- 年龄：25岁'}, 'index': 0, 'finish_reason': 'length'}], 'usage': {'prompt_tokens': 2, 'completion_tokens': 5, 'total_tokens': 7}}
#其中mesage字段，如果命中func
{
    "role": "assistant",
    "content": null,
    "function_call": {
        "name": "send_email",
        "arguments": {
            "receiver": "小美",
            "content": "小美，晚上我不回家吃饭了，你自己解决吧。"
        }
    }
}
#如果没有命中就没有function_call字段
{'role': 'user', 'content': '从您提供的信息中可以提取出如下涉及Jason年龄的信息：\n- Jason：\n\t- 年龄：25岁'}

functions=[
                {
                    "name": "attractionRecommend",
                    "description": "景点推荐",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "地址信息，包括省市、街道、门牌号等"
                                },
                            "expect_distance": {
                                "type": "int",
                                "description": "距离"
                                }
                            },
                        "required": ["location"]
                        },
                    "responses": {
                        "type": "object",
                        "properties": {
                            "price": {
                                "type": "int",
                                "description": "景点距离"
                                },
                            "food": {
                                "type": "string",
                                "description": "景点名称"
                                },
                            },
                        },
                 },
                 {
                        "name": "attractionReservation",
                        "description": "景点介绍预约",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                
                                "attraction": {
                                    "type": "string",
                                    "description": "景点名称"
                                    },
                                },
                            "required": ["attraction"]
                            },
                        "responses": {
                            "type": "object",
                            "properties": {
                                "result": {
                                    "type": "string",
                                    "description": "回答完成"
                                    },
                                }
                            },
                   }
                 ]

流程：
用户提问 → API如果搞的定，则直接回答 → 用户收到
用户提问 → API如果搞不定，则向“外援”求助 → Function Calling回答 → OpenAI API收到然后润色 → 用户收到

# 例子
import openai
import json

openai.api_key = "改成你自己的API_KEY"

# 用户问：“这TM谁啊？？”
messages = [
    {"role": "user", "content": "Who is snakeninny?"}
]

# 第三方函数，这里我是本地调用，不联网；当然你可以改代码，联网
def who_is_snakeninny(value):
    if value == "snakeninny":
        result = {"result" : "He's an AI n00b."}
    elif value == "大名狗剩":
        result = {"result" : "He's an AI h0bby1st."}
    elif value == "沙梓社":
        result = {"result" : "He's an AI enthus1ast."}
    else:
        result = {"result" : "I don't know him."}
    return json.dumps(result) # 官方文档里的返回值格式是JSON

# 第三方函数的介绍，供AI理解和使用
who_is_snakeninny_description = {
    "name": "who_is_snakeninny",
    "description": "Describe snakeninny", # 这个函数是干嘛的
    "parameters": {
        "type": "object",
        "properties": {
            "value": {
                "type": "string",
                "description": "The name of a person", # 这个参数是干嘛的
            }
        },
        "required": ["value"],
    },
}

# 调用API，把第三方函数作为参数传给模型
def get_completion(messages):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613", # 模型可选，目前有gpt-4-0613和gpt-3.5-turbo-0613
        messages=messages, # 其实就是prompt
        functions=[who_is_snakeninny_description], # 如果需要“外援”，就需要这个参数。如果没有这个参数，就不会调用“外援”
    )
    return completion

first_response = get_completion(messages)

# 关注返回值
finish_reason = first_response["choices"][0]["finish_reason"]
message = first_response["choices"][0]["message"] # 其实就是completion

if finish_reason == "stop": # 这时模型可以自己hold住，不需要“外援”
    content = message["content"] # 可以直接返回给用户了
elif finish_reason == "function_call": # 模型感觉自己hold不住，需要“外援”上场
    function_call = message["function_call"]

    function_name = function_call["name"] # 第三方函数名
    function = locals()[function_name] # 第三方函数

    arguments = function_call["arguments"] # 第三方函数的参数名
    name = json.loads(arguments)["value"] # 第三方函数的参数

    function_response = function(name) # 调用第三方函数拿到的返回值

    messages.append(message) # 上下文的固定用法
    messages.append( # 上下文固定用法
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
    )
    
    second_response = get_completion(messages) # 再次调用API，模型根据我们收集的messages再次组织语言
    message = second_response["choices"][0]["message"]
    content = message["content"] # 可以直接返回给用户了

print(content)
##### 开始编码
from langchain.tools import format_tool_to_openai_function
# Swagger 提供一系列免费开源的OpenAPI 相关的工具


# 文心一言的 function_calling功能
# https://yuque.antfin-inc.com/sjsn/biz_interface/aiwgzrmbvgxy3c8p

# gpt的function_calling 功能
# 看queryconditions内部参数：https://yuque.antfin-inc.com/sjsn/biz_interface/ge1fgfafwcg2gxhr 