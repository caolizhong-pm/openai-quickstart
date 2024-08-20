import os, openai
from langchain_community.chat_models.zhipuai import ChatZhipuAI
from langchain.chains import LLMChain

from utils import LOG
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

# adapt to custom API
openai.api_base = "https://nvdc-prod-euw-llmapiorchestration-app.azurewebsites.net/v1/"
headers = {
    "accept": "*/*",
    "Content-Type": "application/json-patch+json",
    "api-key": os.environ.get("ZHIPUAI_API_KEY"),
}

class TranslationChain:
    def __init__(self, model_name: str = "glm-4", verbose: bool = True): 
        
        # 翻译任务指令始终由 System 角色承担
        template = (
            """You are a translation expert, proficient in various languages. \n
            Translates {source_language} to {target_language} with {style} style."""
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        # 待翻译文本由 Human 角色输入
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        # 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        # 为了翻译结果的稳定性，将 temperature 设置为 0
        chat = ChatZhipuAI(
                model_name=model_name, base_url=openai.api_base, temperature=0, max_tokens=2048, verbose=verbose, default_headers=headers) # clz adaption
        #self.chain = chat_prompt_template | chat # clz
        self.chain = LLMChain(llm=chat, prompt=chat_prompt_template, verbose=verbose)

    def run(self, text: str, source_language: str, target_language: str, style: str) -> (str, bool):
        result = ""
        try:
            result = self.chain.run({
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
                "style": style,
            })
        except Exception as e:
            LOG.error(f"An error occurred during translation: {e}")
            return result, False

        return result, True
