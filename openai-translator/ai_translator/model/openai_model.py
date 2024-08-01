import requests
import simplejson
import time
import os
import openai

from model import Model
from utils import LOG
from openai import OpenAI

class OpenAIModel(Model):
    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI(base_url="https://myapp.azurewebsites.net/v1/")  # replace with real azure openai host!!!

    def make_request(self, prompt):
        headers = {
            "accept": "*/*",
            "workspaceName": "VR0312RANBTSPackageBuildErrorAutodetectionAndTrunk",
            "Content-Type": "application/json-patch+json",
            "api-key": os.environ.get("OPENAI_API_KEY"),
        }
        attempts = 0
        while attempts < 3:
            try:
                if self.model.startswith(("gpt-4", "gpt-3.5")):
                    response = self.client.chat.completions.create(
                        extra_headers=headers,
                        model=self.model,
                        max_tokens=850,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    translation = response.choices[0].message.content.strip()
                else:
                    response = self.client.completions.create(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0
                    )
                    translation = response.choices[0].text.strip()

                return translation, True
            except openai.RateLimitError as e:
                attempts += 1
                if attempts < 3:
                    LOG.warning("Rate limit reached. Waiting for 60 seconds before retrying.")
                    time.sleep(60)
                else:
                    raise Exception("Rate limit reached. Maximum attempts exceeded.")
            except openai.APIConnectionError as e:
                print("The server could not be reached")
                print(e.__cause__)  # an underlying Exception, likely raised within httpx.            except requests.exceptions.Timeout as e:
            except openai.APIStatusError as e:
                print("Another non-200-range status code was received")
                print(e.status_code)
                print(e.response)
            except Exception as e:
                raise Exception(f"发生了未知错误：{e}")
        return "", False
