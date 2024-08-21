import os, requests, time, jwt
from api import generate_token, get_chatglm_response_via_sdk
def first_chat(user1:str, user2:str, topic:str):
    api_key = os.environ["ZHIPUAI_API_KEY"]
    token = generate_token(api_key, 60)
    first_message_template = [
        {"role": "system", "content": f"你是{user1}，基于{topic}的主题跟{user2}开展对话"},
        {"role": "user", "content": "你只对他说一句话，只输出话语本身而不包含人物"}
    ]

    print(first_message_template)
    full_content = ""
    for content in get_chatglm_response_via_sdk(first_message_template):
        full_content += content
    #print(full_content)
    return full_content

def user_response(user1:str, user2:str, last_message:str):
    api_key = os.environ["ZHIPUAI_API_KEY"]
    token = generate_token(api_key, 60)    
    response_message_template = [
        {"role": "system", "content": f"你是{user1}，在跟{user2}对话"},
        {"role": "user", "content": f"针对{last_message}进行回复，你只回复一句话而不是复述{last_message}"}
    ]
    print(response_message_template)
    full_content = ""
    for content in get_chatglm_response_via_sdk(response_message_template):
        full_content += content
    #print(full_content)
    return full_content

""" res = get_chatglm_response_via_sdk([{'role': 'system', 'content': '你是猪八戒，基于"是的，八戒，我们每个人都有自己的长处和短处，只要我们齐心协力，就能保护师傅，完成取经大业。"回应孙悟空'}, {'role': 'user', 'content': '你只说一句话，只输出话语本身'}])
full_content = ""
for content in res:
    #print(content)
    full_content += content """