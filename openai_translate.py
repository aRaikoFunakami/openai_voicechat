import openai
import json
import os
import sys
import logging
import langid
import unicodedata

# List of ISO 639-1 codes
# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
#
ISO639 = {
    'ja': 'Japanese',
    'en': 'English',
    'zh': 'Chinese',
    'ko': 'Korean',
}
defualt_language = 'English'

def lang_name(id):
    print(id)
    return ISO639.get(id, defualt_language)

def translate_text(input, out_lang = 'ja'):
    load_config()
    input_lang = ISO639.get(langid.classify(input)[0], defualt_language)
    out_lang = ISO639.get(out_lang, defualt_language)
    
    # lang に翻訳する
    if input_lang == out_lang:
        return input
    
    logging.info('text:%s from:%s, to:%s', input, input_lang, out_lang) 
    completion = openai.ChatCompletion.create(
			# モデルを選択
			model     = "gpt-3.5-turbo-0613",
			# メッセージ
			messages  = [
					{"role": "system", "content": f'You are a helpful assistant that translates {input_lang} to {out_lang}.'},
					{"role": "user", "content": f'Translate the following {input_lang} text to {out_lang} :{input}. And Output only translated text'}
					] ,
			max_tokens  = 1024,             # 生成する文章の最大単語数
			n           = 1,                # いくつの返答を生成するか
			stop        = None,             # 指定した単語が出現した場合、文章生成を打ち切る
			temperature = 0,                # 出力する単語のランダム性（0から2の範囲） 0であれば毎回返答内容固定
		)
    text = completion.choices[0].message.content
    return text


test_texts = [
    ['Hello, how are you?', 'ja'],
    ['I love eating sushi.', 'en'],
    ['こんにちは、元気ですか？', 'zh'],
    ['寿司を食べるのが大好きです。', 'ja'],
    ['你好，你好吗？', 'en'],
    ['我喜欢吃寿司。', 'zh'],
]

# load config
def load_config():
    config_file = os.path.dirname(__file__) + "/config.json"
    config = None
    with open(config_file, 'r') as file:
        config = json.load(file)
    openai.api_key = config["openai_api_key"]
    return config

def main():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(filename)s:%(funcName)s[%(lineno)d] - %(message)s",
    )
    for test in test_texts:
        print(f'{test[0]} to [{test[1]}] {translate_text(test[0], test[1])}')

if __name__ == '__main__':
    main()