import openai
import json
import os
import logging
import urllib.parse

#
# Config
#
model = "gpt-3.5-turbo-0613"


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
def get_applemusic_info(keyword):
    logging.info("keyword %s", keyword)
    baseurl = "https://music.apple.com/jp/search?term="
    # baseurl = "https://open.spotify.com/search/"
    url = baseurl + urllib.parse.quote(keyword)
    logging.info("url %s", url)
    return url


applemusic_function = {
    "name": "get_applemusic_info",
    "description": "Play songs and Search for songs to be played on apple music by keywords related to songs, such as singer's name or song title.",
    "parameters": {
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "Keywords related to the song, such as the singer's name or song title",
            },
        },
        "required": [
            "keyword",
        ],
    },
}


def call_defined_function(message):
    function_name = message["function_call"]["name"]
    logging.debug("選択された関数を呼び出す: %s", function_name)
    arguments = json.loads(message["function_call"]["arguments"])
    if function_name == "get_applemusic_info":
        keyword = arguments.get("keyword")
        return get_applemusic_info(keyword)
    else:
        return None


def non_streaming_chat(text):
    # 関数と引数を決定する
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": text}],
            functions=[applemusic_function],
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


def chat(text):
    logging.debug(f"chatstart:{text}")
    config = load_config()
    openai.api_key = config["openai_api_key"]
    # situation = guess_situation(text)
    # q = guess_template.format(situation, text)
    q = template.format(text)
    return non_streaming_chat(q)


template = """'
条件:
- 50文字以内で回答せよ

入力文:
{}
"""


queries = [
    ["尾崎豊のI love youの曲を聴きたい", "get_applemusic_info"],
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
