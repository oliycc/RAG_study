# 基于文本生成接口，实现openAI的Function calling功能
# openAI的Function calling功能:
# 入参：{'messages': [{'role': 'user', 'content': '提取信息 Jason今年25岁'}], 'model': 'gpt-3.5', 'function_call': {'name': 'UserDetail'}, 'functions': [{'name': 'UserDetail', 'description': 'Correctly extracted `UserDetail` with all the required parameters with correct types', 'parameters': {'properties': {'name': {'title': 'Name', 'type': 'string'}, 'age': {'title': 'Age', 'type': 'integer'}}, 'required': ['age', 'name'], 'type': 'object'}}]}
# 出参: 