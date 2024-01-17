import time
import SparkApi
import customer_llm_api as gptApi
from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

#用于配置大模型版本，默认“general/generalv2”
# domain = "general"   # v1.5版本
#domain = "generalv2"    # v2.0版本
#domain = "generalv3"    # v3.0版本
#云端环境的服务地址
# Spark_url = "ws://spark-api.xf-yun.com/v1.1/chat"  # v1.5环境的地址
#Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址
#Spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"  # v3.0环境的地址
# modal_dict={"general":"ws://spark-api.xf-yun.com/v1.1/chat",
#             "generalv2":"ws://spark-api.xf-yun.com/v2.1/chat",
#             "generalv3":"ws://spark-api.xf-yun.com/v3.1/chat"
#             }


def getText(role,content):
    text =[]
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

class CustomLLM(LLM):
    appid: Optional[str] = None
    api_secret: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None

    @property
    def _llm_type(self) -> str:
        return "CustomLLM"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        question = getText("user",prompt)
        ## 调用llm
        # Spark_url = modal_dict[self.model]
        # domain = self.model
        # SparkApi.answer = ""
        # SparkApi.main(self.appid,self.api_key,self.api_secret,Spark_url,domain,question)
        # return SparkApi.answer
        # print(f'CustomLLM##question={question}')
        retry = 5
        output = None
        content = None
        while not content and retry>0:
            try:
                output = gptApi.customer_gpt_api(question, model='WENXIN')
                content = output.get('content', None)
                print(f'__call##content={content}')
            except Exception as e:
                pass
            retry -=1
            time.sleep(3)
        print('done')
        if content==None:
            raise Exception('CustomLLM##调用结果为空, output='+output.get('content', ''))
        return content

    # @property
    # def _identifying_params(self) -> Mapping[str, Any]:
    #     """Get the identifying parameters."""
    #     return {"appid": self.appid}