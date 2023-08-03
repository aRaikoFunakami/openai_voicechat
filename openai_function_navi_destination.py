import json
import os, logging
from typing import Any

import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import requests

"""
langchainのConversationalRetrievalChain.from_llmを利用する場合にはgpt-4でないと良い回答が得られない
"""
model_name = "gpt-3.5-turbo-0613"
# model_name = "gpt-4-0613"

# default_persist_directory = "./chroma_split_documents"
default_persist_directory = "./chroma_load_and_split"


# load config
def load_config():
    config_file = os.path.dirname(__file__) + "/config.json"
    config = None
    with open(config_file, "r") as file:
        config = json.load(file)
    return config


#
# call by openai functional calling
#
def get_navi_destination_info(destinations):
    logging.info('destinations:%s', destinations)
    return destinations


#
# call by openai functional calling
#
# function call - arrays as Parameters
# https://community.openai.com/t/function-call-arrays-as-parameters/268008
#
#
navi_destination_function = {
    "name": "get_navi_destination_info",
    "description": "Set intermediate points and destinations by landmark in the car navigation system.",
    "parameters": {
        "type": "object",
        "properties": {
            "destinations": {
                "type": "array",
                "description": "Start point, intermediate point (0 or more), goal point",
                "items": {
                    "type": "string",
                },
            },
        },
        "required": ["destinations"],
    },
}
#
#
# Test codes: Verify that the registered function call is called as expected
#
#


def call_defined_function(message):
    function_name = message["function_call"]["name"]
    logging.info("選択された関数を呼び出す: %s", function_name)
    
    arguments = json.loads(message["function_call"]["arguments"])
    if function_name == "get_navi_destination_info":
        return get_navi_destination_info(
            destinations = arguments.get("destinations")
        )
    else:
        return None


def non_streaming_chat(text):
    # 関数と引数を決定する
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "user", "content": text}],
            functions=[navi_destination_function],
            function_call="auto",
        )
    except openai.error.OpenAIError as e:
        error_string = f"An error occurred: {e}"
        print(error_string)
        return {"response": error_string, "finish_reason": "stop"}

    message = response["choices"][0]["message"]
    logging.debug("message: %s", message)
    # 選択した関数を実行する
    if message.get("function_call"):
        function_response = call_defined_function(message)
        #
        # Returns the name of the function called for unit test
        #
        return message["function_call"]["name"]
    else:
        return "chatgpt"


template = """
条件:
- 50文字以内で回答せよ

入力文:
{}
"""


def chat(text):
    logging.debug(f"chatstart:{text}")
    config = load_config()
    openai.api_key = config["openai_api_key"]
    q = template.format(text)
    return non_streaming_chat(q)


queries = [
    ["カーナビで行き先を設定したい。秋葉原駅にいます。一番近くの中華屋に寄って横浜駅に向かいたい", "get_navi_destination_info"],
    ["カーナビで行き先を設定したい。秋葉原駅にいます。銀座三越にひょって寄って横浜駅に向かいたい", "get_navi_destination_info"],
]


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(filename)s:%(funcName)s[%(lineno)d] - %(message)s",
    )
    for query in queries:
        response = chat(query[0])
        print(f"[{query[1] == response}] 期待:{query[1]}, 実際:{response}, 質問:{query[0]}")


if __name__ == "__main__":
    main()
