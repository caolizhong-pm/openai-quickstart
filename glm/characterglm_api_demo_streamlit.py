"""
一个简单的demo，调用CharacterGLM实现角色扮演，针对用户给定的主题进行自动对话。

依赖：
pyjwt
requests
streamlit
zhipuai
python-dotenv

运行方式：
```bash
streamlit run characterglm_api_demo_streamlit.py
```
"""
import os, time
import itertools
from typing import Iterator, Optional
import io, csv

import streamlit as st
from dotenv import load_dotenv
# 通过.env文件设置环境变量
# reference: https://github.com/theskumar/python-dotenv
load_dotenv()

import api
from api import generate_chat_scene_prompt, generate_role_appearance, get_characterglm_response, generate_cogview_image, get_chatglm_response_via_sdk
from data_types import TextMsg, ImageMsg, TextMsgList, MsgList, filter_text_msg
from generate_response import first_chat, user_response
st.set_page_config(page_title="CharacterGLM API Demo", page_icon="🤖", layout="wide")
debug = os.getenv("DEBUG", "").lower() in ("1", "yes", "y", "true", "t", "on")


def update_api_key(key: Optional[str] = None):
    if debug:
        print(f'update_api_key. st.session_state["API_KEY"] = {st.session_state["API_KEY"]}, key = {key}')
    key = key or st.session_state["API_KEY"]
    if key:
        api.API_KEY = key

# 设置API KEY
api_key = st.sidebar.text_input("API_KEY", value=os.getenv("ZHIPUAI_API_KEY", ""), key="API_KEY", type="password", on_change=update_api_key)
update_api_key(api_key)


# 初始化
if "history" not in st.session_state:
    st.session_state["history"] = []
#if "current_role" not in st.session_state:
    st.session_state["current_role"] = "user"
    st.session_state["prompt"] = f""
if "meta" not in st.session_state:
    st.session_state["meta"] = {
        "user_info": "",
        "bot_info": "",
        "bot_name": "",
        "user_name": "",
        "topic": "",
        "dial_turns": 2
    }


def init_session():
    st.session_state["history"] = []


# 4个输入框，设置meta的4个字段
meta_labels = {
    "bot_name": "角色名",
    "user_name": "用户名", 
    "bot_info": "角色人设",
    "user_info": "用户人设",
    "topic": "对话主题",
    "dial_turns": "对话轮数"
}

# 2x2 layout
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input(label="角色名", key="bot_name", on_change=lambda : st.session_state["meta"].update(bot_name=st.session_state["bot_name"]), help="模型所扮演的角色的名字，不可以为空")
        st.text_area(label="角色人设", key="bot_info", on_change=lambda : st.session_state["meta"].update(bot_info=st.session_state["bot_info"]), help="角色的详细人设信息，不可以为空")
        
    with col2:
        st.text_input(label="用户名", value="", key="user_name", on_change=lambda : st.session_state["meta"].update(user_name=st.session_state["user_name"]), help="用户的名字，默认为用户")
        st.text_area(label="用户人设", value="", key="user_info", on_change=lambda : st.session_state["meta"].update(user_info=st.session_state["user_info"]), help="用户的详细人设信息，可以为空")
    with col3:
        st.text_input(label="聊天主题", key="topic", on_change=lambda : st.session_state["meta"].update(topic=st.session_state["topic"]), help="模型的聊天主题")
        st.text_input(label="对话轮数", key="dial_turns", on_change=lambda : st.session_state["meta"].update(topic=st.session_state["dial_turns"]), help="模型的聊天轮数")

def verify_meta() -> bool:
    # 检查`角色名`和`角色人设`是否空，若为空，则弹出提醒
    if st.session_state["meta"]["bot_name"] == "" or st.session_state["meta"]["bot_info"] == "":
        st.error("角色名和角色人设不能为空")
        return False
    else:
        return True

def output_stream_response(response_stream: Iterator[str], placeholder):
    content = ""
    for content in itertools.accumulate(response_stream):
        placeholder.markdown(content)
    return content


button_labels = {
    #"clear_meta": "清空人设",
    "clear_history": "清空对话历史",
    #"gen_picture": "生成图片",
    "download_chat": "下载对话",
    "start_chat": "开始对话"
}
if debug:
    button_labels.update({
        "show_api_key": "查看API_KEY",
        "show_meta": "查看meta",
        "show_history": "查看历史"
    })

# 在同一行排列按钮
with st.container():
    n_button = len(button_labels)
    cols = st.columns(n_button)
    button_key_to_col = dict(zip(button_labels.keys(), cols))
    
    with button_key_to_col["download_chat"]:
        download_chat = st.button(button_labels["download_chat"], key="download_chat")
    with button_key_to_col["start_chat"]:
        start_chat = st.button(button_labels["start_chat"], key="start_chat")
    with button_key_to_col["clear_history"]:
        clear_history = st.button(button_labels["clear_history"], key="clear_history")
        if clear_history:
            init_session()
            st.rerun()

    if debug:
        with button_key_to_col["show_api_key"]:
            show_api_key = st.button(button_labels["show_api_key"], key="show_api_key")
            if show_api_key:
                print(f"API_KEY = {api.API_KEY}")
        
        with button_key_to_col["show_meta"]:
            show_meta = st.button(button_labels["show_meta"], key="show_meta")
            if show_meta:
                print(f"meta = {st.session_state['meta']}")
        
        with button_key_to_col["show_history"]:
            show_history = st.button(button_labels["show_history"], key="show_history")
            if show_history:
                print(f"history = {st.session_state['history']}")



# 展示对话历史
for msg in st.session_state["history"]:
    if msg["role"] == "user":
        with st.chat_message(name="user", avatar="user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message(name="assistant", avatar="assistant"):
            st.markdown(msg["content"])
    elif msg["role"] == "image":
        with st.chat_message(name="assistant", avatar="assistant"):
            st.image(msg["image"], caption=msg.get("caption", None))
    else:
        raise Exception("Invalid role")


if download_chat:  # new function
    # Check if "history" exists in session_state
    if "history" in st.session_state:
        history_data = st.session_state["history"]

        # Extract fieldnames from all dictionaries
        fieldnames = set()
        for entry in history_data:
            fieldnames.update(entry.keys())
        fieldnames = list(fieldnames)

        # Create a CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for entry in history_data:
            # Ensure all keys are present
            row = {key: entry.get(key, "") for key in fieldnames}
            writer.writerow(row)
        csv_data = output.getvalue()

        # Create a download button for the history file
        st.download_button(
            label="Download History as CSV",
            data=csv_data,
            file_name="history.csv",
            mime="text/csv; charset=utf-8"  # 确保指定UTF-8编码
        )
    else:
        st.write("No history found in session state.")    
with st.chat_message(name="user", avatar="user"):
    input_placeholder = st.empty()
with st.chat_message(name="assistant", avatar="assistant"):
    message_placeholder = st.empty()

if start_chat:

    st.session_state["current_role"] = "user"  # 初始角色
    query = first_chat(st.session_state["user_name"], st.session_state["bot_name"], st.session_state["topic"])
    input_placeholder.markdown(query)
    st.session_state["history"].append(TextMsg({"role": st.session_state["current_role"], "content": query}))
    print(st.session_state["history"])
    #query = output_stream_response(query, message_placeholder)
    #query = st.chat_input("悟空")
    num_dialogue = int(st.session_state["dial_turns"])
    print(num_dialogue)

    for turn in range(num_dialogue):
        if query:
            time.sleep(3)
            if not verify_meta():
                st.error("未设置人物")
            if not api.API_KEY:
                st.error("未设置API_KEY")

            #input_placeholder.markdown(query)
            response_stream = get_characterglm_response(filter_text_msg(st.session_state["history"]), meta=st.session_state["meta"])
            response = output_stream_response(response_stream, message_placeholder)
            time.sleep(3)
            if not response:
                message_placeholder.markdown("生成出错")
                print("no response")
                st.session_state["history"].pop()
            else:
                st.session_state["history"].append(TextMsg({"role": "assistant", "content": response})) 
                print(st.session_state["history"])
                next_query = user_response(st.session_state["user_name"], st.session_state["bot_name"], response)
                st.session_state["history"].append(TextMsg({"role": "user", "content": next_query}))
                query = next_query

