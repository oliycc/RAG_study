# reAct框架和简单工具使用
import os
import re
import json
from typing import List, Union
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import StringPromptTemplate
# from langchain impor                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     t OpenAI, SerpAPIWrapper, LLMChain
from langchain import SerpAPIWrapper, LLMChain
from langchain.schema import AgentAction, AgentFinish

os.environ["OPENAI_API_KEY"] = "你的OpenAI key" ## 如果你直接购买了gpt产品

# case_reAct: https://python.langchain.com.cn/docs/modules/agents/how_to/custom_llm_agent
# 让自定义llm做推理决策，调用工具（api），llm整合工具调用结果，实现输出


def find_person(name: str):
    print(f'执行工具#find_person, name={name}')
    """
    模拟本地数据库查询。

    Args:
        name (str): 人物名称，由LLM提取。

    Returns:
        _type_: _description_
    """
    info = {
        '张三': '男',
        '小红': '女'
    }
    return info.get(name, f'未知')


def recommend_item(gender: str):
    print(f'执行工具#recommend_item, gender={gender}')
    """
    根据人物性别推荐不同的商品。

    Args:
        gender (str): 人物的性别，由 LLM 提取。

    Returns:
        _type_: _description_
    """
    recommend = {
        '男': ['Steam爆款', 'RTX-9090', 'iPhone 80'],
        '女': ['夏季碎花裙', '轻盈帆布包', '琉璃唇釉'],
        '未知': ['AJ新品', '手冲咖啡']
    }
    return recommend.get(gender, f'未找到合适的推荐商品，那随便买些什么吧，只要消费就能快乐！')

tools = [
    Tool(
        name = "查询人物性别",
        func=find_person,
        description="通过人名查找该人物的性别时用的工具，输入应该是人物的名字"
    ),
    Tool(
        name = "根据性别推荐商品",
        func=recommend_item,
        description="当知道了一个人性别后想进一步获得他可能感兴趣的商品时用的工具，输入应该是人物的性别"
    )
]

## 定义COT中文模版
SLIP_KEY = '等待返回'  # 防止observe虚构
template_zh = """按照给定的格式回答以下问题。你可以使用下面这些工具：

{tools}

整个流程需要遵循以下用---括起来的格式：
---
Question: 我需要回答的问题
Thought: 回答这个上述我需要做些什么
Action: ”{tool_names}“ 中的其中一个工具名
Action Input: 选择工具所需要的输入
Observation: 工具返回的结果（固定值为”等待返回“，等待其他系统返回结果，终止输出）
...（这个思考/行动/行动输入/观察可以重复N次）
Thought: 我现在知道最终答案
Final Answer: 原始输入问题的最终答案
---

要求：
1.Action只能用{tool_names}中的一个，禁止编造工具，不能采用其他工具
2.充分使用已有的相关工具
3.Observation禁止猜测，固定为”等待返回“，中断输出
4. 最终答案必须放在Final Answer字段，回答内容不要透露工具使用逻辑
现在开始回答，记得在给出最终答案前多按照指定格式进行一步一步的推理。
5. 如果Question和工具无关，{allow_direct_ans}直接根据Question输出Final Answer
Question: {input}
{agent_scratchpad}
"""

# 是否允许直接回答
ALLOW_DIRECT_ANS = True
class CustomPromptTemplate(StringPromptTemplate):
    template: str           # 标准模板
    tools: List[Tool]       # 可使用工具集合
    
    def format(
            self, 
            **kwargs
        ) -> str:
        ### ***难点1： 健壮的prompt（不然存在：工具调用不充分，幻想工具返回，格式不符合预期），多次调试确保健壮性
        """
        按照定义的 template，将需要的值都填写进去。

        Returns:
            str: 填充好后的 template。
        """
        intermediate_steps = kwargs.pop("intermediate_steps")       # 取出中间步骤并进行执行
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += get_current_step(action)  ## 不能
            thoughts += f"Observation: {observation}\nThought: "
        kwargs["agent_scratchpad"] = thoughts                       # 记录下当前想法
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])    # 枚举所有可使用的工具名+工具描述
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])                        # 枚举所有的工具名称
        kwargs["allow_direct_ans"] = '允许' if ALLOW_DIRECT_ANS else '不允许'
        cur_prompt = self.template.format(**kwargs)
        print(cur_prompt)
        return cur_prompt
    

# # 从中间步骤获得, llm输出出现幻觉，只取第一个Thought，Action，Action Input
def get_current_step(action):
    str_output = action.log
    thought_pattern = re.compile(r'"*\s*Thought"*\s*:\s*"*(.*)"*\s*')
    action_pattern = re.compile(r'"*\s*Action"*\s*:\s*"*(.*)"*\s*')
    input_pattern = re.compile(r'"*\s*Action\s*Input"*\s*:\s*"*\s*(.*)"*\s*')
    observation_pattern = re.compile(r'"*\s*Observation"*\s*:\s*"*\s*(.*)"*\s*')
    Thought_list = thought_pattern.findall(str_output)
    Action_list = action_pattern.findall(str_output)
    Input_list = input_pattern.findall(str_output)
    Observation_list = observation_pattern.findall(str_output)
    thought = Thought_list[0]
    action = rm_punctuation(Action_list[0])
    action_input = rm_punctuation(Input_list[0])

    step = f'Thought: {thought}\nAction: {action}\nAction Input: {action_input}\n'
    return step
    


# 去除字符串中所有标点符号
import string
import re
# 去除符号
def rm_punctuation(text):
    # 定义需要移除的标点符号字符串
    punctuation = string.punctuation
    # 创建正则表达式模式，匹配任何标点符号
    regex_pattern = f'[{re.escape(punctuation)}]'
    # 使用 re.sub() 函数替换字符串中的标点符号为空字符串（即移除它们）
    clean_text = re.sub(regex_pattern, '', text)
    return clean_text.replace(' ','')


# 使用用户自定义模版
prompt = CustomPromptTemplate(
    template=template_zh,
    tools=tools,
    input_variables=["input", "intermediate_steps"]
)

# 解析llm的决策，执行动作
class CustomOutputParser(AgentOutputParser):
    def parse(
            self, 
            llm_output: str
        ) -> Union[AgentAction, AgentFinish]:
        print('CustomOutputParser##starting.....')
        """
        解析 llm 的输出，根据输出文本找到需要执行的决策。

        Args:
            llm_output (str): _description_

        Raises:
            ValueError: _description_

        Returns:
            Union[AgentAction, AgentFinish]: _description_
        """
        if SLIP_KEY in llm_output:
            llm_output = llm_output.split(SLIP_KEY)[0]
            regex = r'Action"*\s*\d*\s*:\s*(.*?)\s*\n\s*"*Action\s*\d*\s*Input"*\s*\d*\s*:\s*[\s]*(.*)'  # 解析 action_input 和 action
            matches = re.findall(regex, llm_output) ## re.DOTALL
            # 获取最后一个匹配结果
            last_match = matches[-1]
            if not last_match:
                raise ValueError(f"Could not parse LLM output: `{llm_output}`")
            action = rm_punctuation(last_match[0])
            action_input = rm_punctuation(last_match[1])
            print(f'CustomOutputParser##action={action}, action_input={action_input}')
            return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
        elif "Final Answer" in llm_output:       # 如果句子中包含 Final Answer 则代表已经完成
            # 正则匹配
            regex = r'Final Answer"*\s*:(.*)'
            match = re.search(regex, llm_output)
            value = match.group(1)  ##  llm_output.split("Final Answer:")[-1].strip()
            return AgentFinish(
                return_values={"output":value},
                log=llm_output,
            )
        else:
            return AgentFinish(
                return_values={"output": llm_output},
                log=llm_output,
            )

    
    


output_parser = CustomOutputParser()

#配置代理
import langchain_study.done_case0_udf_llm_api as done_case0_udf_llm_api
llm = done_case0_udf_llm_api.CustomLLM()
llm_chain = LLMChain(
    llm=llm, 
    prompt=prompt
)
tool_names = [tool.name for tool in tools]

# 单个操作代理
agent = LLMSingleActionAgent(
    llm_chain=llm_chain, 
    output_parser=output_parser,
    stop=["\nObservation:"], 
    allowed_tools=tool_names
)



# 配置执行器
agent_executor = AgentExecutor.from_agent_and_tools(
    # llm=llm,
    agent=agent, 
    tools=tools, 
    verbose=True
)

# 测试这个问题
res = agent_executor.run(
    "小红的爸爸过生日，我应该送什么给他呢"
    #  "我晚上睡不着觉，好烦啊"
)
print(res)




# if __name__ == "__main__":
#         llm_output = """
# '```json\n{\n    "Thought": "首先，我需要了解张三的性别才能为其推荐合适的礼物。",\n    "Action": "查询人物性别",\n    "Action Input": "张三",\n    "Observation": "张三是男性。",\n    "Thought": "现在我已经知道了张三是男性，接下来我可以根据这个信息为其推荐礼物。",\n    "Action": "根据性别推荐商品",\n    "Action Input": "男性",\n    "Observation": "对于男性，可以考虑送他电子产品、运动装备、酒类或者男士护肤品等礼物。",\n    "Thought": "结合张三的年龄和职业，我可以进一步筛选推荐的商品。",\n    "Action": "查询人物年龄和职业",\n    "Action Input": "张三",\n    "Observation": "张三是一位30岁的工程师。",\n    "Thought": "考虑到张三是一位30岁的工程师，他可能会更喜欢实用性强且符合其职业特点的礼物。",\n    "Action": "根据年龄和职业进一步筛选推荐商品",\n    "Action Input": "30岁工程师",\n    "Observation": "对于30岁的工程师，可以考虑送他一款高质量的笔记本电脑、专业书籍、智能手表或者高品质的咖啡机等礼物。",\n    "Thought": "综合考虑，我认为送张三一款高质量的笔记本电脑是一个不错的选择，既符合他的职业需求，也能满足他的个人喜好。",\n    "Final Answer": "建议送张三一款高质量的笔记本电脑作为礼物。"\n}\n```'
# """
#         regex = r'Action"*\s*\d*\s*:\s*(.*?)\s*\n\s*"*Action\s*\d*\s*Input"*\s*\d*\s*:\s*[\s]*(.*)'  # 解析 action_input 和 action
#         match = re.search(regex, llm_output, re.DOTALL)
#         if not match:
#             raise ValueError(f"Could not parse LLM output: `{llm_output}`")
#         action = match.group(1).strip()
#         action_input = match.group(2)
#         print(f'action={action}, action_input={action_input}')