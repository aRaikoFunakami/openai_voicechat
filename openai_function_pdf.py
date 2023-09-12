import json
import os, logging
from typing import Any

import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import markdown


"""
langchainのConversationalRetrievalChain.from_llmを利用する場合にはgpt-4でないと良い回答が得られない
"""
model_name = "gpt-3.5-turbo-0613"
# model_name = "gpt-4-0613"

# default_persist_directory = "./chroma_split_documents"
# default_persist_directory = "./chroma_load_and_split"
default_persist_directory = "./chroma_viera"

# TODO
# - pdf の URL をget_pdf_info で返すようにする
# - langchain 側でそのURLをクライアントに返す
# {
#    '...pdf': {'title':'説明', 'url':'URL'},
#    '...pdf': ...,
# }
# html
pdf_baseurl = "http://127.0.0.1:8080"
pdf_titles = {
    "th_75_65_55lx950_em.pdf": {
        "title": "操作ガイド",
        "url": f"{pdf_baseurl}/th_75_65_55lx950_em.pdf",
    },
    "th_75_65_55lx950.pdf": {
        "title": "取扱説明書",
        "url": f"{pdf_baseurl}/th_75_65_55lx950.pdf",
    },
    "NX350-NX250_MM_JP_M78364N_1_2303.pdf": {
        "title": "マルチメディア取扱説明書",
        "url": f"{pdf_baseurl}/NX350-NX250_MM_JP_M78364N_1_2303.pdf",
    },
    "NX350-NX250_OM_JP_M78364V_1_2303.pdf": {
        "title": "取扱説明書",
        "url": f"{pdf_baseurl}/NX350-NX250_OM_JP_M78364V_1_2303.pdf",
    },
    "NX350-NX250_UG_JP_M78364_1_2303.pdf": {
        "title": "ユーザーガイド",
        "url": f"{pdf_baseurl}/NX350-NX250_UG_JP_M78364_1_2303.pdf",
    },
}


# load config
def load_config():
    config_file = os.path.dirname(__file__) + "/config.json"
    config = None
    with open(config_file, "r") as file:
        config = json.load(file)
    return config


def source_urls(docs):
    urls = []
    for doc in docs:
        # page should be +1 because of start page is 0
        page = doc.metadata["page"] + 1
        # source pdf file to Subject
        source = doc.metadata.get("source")
        for key in pdf_titles.keys():
            if key in source:
                url = pdf_titles[key]["url"] + "#page=" + str(page) + "&view=Fit"
                urls.append(url)
    return urls


def source_string(docs):
    result = {}
    for doc in docs:
        # source pdf file to Subject
        source = doc.metadata.get("source")
        for key in pdf_titles.keys():
            if key in source:
                # doc.metadata['source'] = pdf_titles[key]['title']
                source = pdf_titles[key]["title"]
                # page should be +1 because of start page is 0
                page = doc.metadata["page"] + 1
        # summarize the reference page with the title of the pdf
        # page = doc.metadata['page']
        # source = doc.metadata.get('source')
        if source not in result:
            result[source] = []

        result[source].append(page)
    # to string
    response = ""
    for source, pages in result.items():
        response = response + f"{source} page.{', '.join(map(str, pages))}" + "\n"
    return response


get_pdf_info_cache_memory = {}


#
# call by openai functional calling
#
def get_pdf_info(query, persist_directory=default_persist_directory):
    logging.info("%s, %s", query, persist_directory)
    # very simple cache
    if get_pdf_info_cache_memory.get(query) is not None:
        logging.info("Hit the cache: %s", query)
        return get_pdf_info_cache_memory[query]
    # initialize OpenAI API
    config = load_config()
    openai.api_key = config["openai_api_key"]
    os.environ["OPENAI_API_KEY"] = openai.api_key
    # vectorsearching with query
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        embedding_function=embeddings, persist_directory=persist_directory
    )
    # 参照するPDFファイルが日本語のため相性を合わせる
    chat_history = []
    llm = ChatOpenAI(temperature=0, model_name=model_name)
    pdf_qa = ConversationalRetrievalChain.from_llm(
        llm, vectorstore.as_retriever(), return_source_documents=True
    )
    result = pdf_qa({"question": query, "chat_history": chat_history})
    # response = result["answer"] + '\n\n' + source_string(result['source_documents'])
    response = {
        "content": result["answer"]
        + "\n\n"
        + source_string(result["source_documents"]),
        "urls": source_urls(result["source_documents"]),
    }
    # response = json.dumps(response, indent=2, ensure_ascii=False)
    logging.info("type: %s, %s", type(response), response)
    get_pdf_info_cache_memory[query] = response
    return response


#
# call by openai functional calling
#
def get_pdf_lexus_info(query, persist_directory="./chroma_lexus"):
    return get_pdf_info(query, persist_directory)


pdf_lexus_function = {
    "name": "get_pdf_lexus_info",
    "description": "車の操作方法、カーナビの使い方、マルチメディアの操作方法を取得します",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "車の操作方法、カーナビの使い方、マルチメディアの操作方法についての質問",
            },
        },
        "required": ["query"],
    },
}


def get_pdf_viera_info(query, persist_directory="./chroma_viera"):
    return get_pdf_info(query, persist_directory)


pdf_viera_function = {
    "name": "get_pdf_viera_info",
    # "description": "インターネットに接続したスマートテレビであるビエラの操作方法を取得します",
    "description": "Search TV instruction manuals. Get how to operate Viera, a smart TV connected to the Internet",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                # "description": "インターネットに接続したスマートテレビであるビエラの操作方法についての質問",
                "description": "Questions about how to operate Viera, a smart TV connected to the Internet",
            },
        },
        "required": ["query"],
    },
}

#
#
# Test codes: Verify that the registered function call is called as expected
#
#


def call_defined_function(message):
    function_name = message["function_call"]["name"]
    logging.debug("選択された関数を呼び出す: %s", function_name)
    arguments = json.loads(message["function_call"]["arguments"])
    if function_name == "get_pdf_viera_info":
        return get_pdf_viera_info(arguments.get("query"))
    elif function_name == "get_pdf_lexus_info":
        return get_pdf_lexus_info(arguments.get("query"))
    else:
        return None


def non_streaming_chat(text):
    # 関数と引数を決定する
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "user", "content": text}],
            functions=[pdf_lexus_function, pdf_viera_function],
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


queries1 = [
    ["カーナビでYouTubeを見たい", "get_pdf_info"],
    ["I want to watch YouTube on my car navigation system.", "get_pdf_info"],
    ["カーナビのWebブラウザでYouTubeを閲覧したいです。", "get_pdf_info"],
    [
        "I would like to browse YouTube on the car navigation system's web browser.",
        "get_pdf_info",
    ],
    ["カーナビでのYouTube閲覧方法を教えてください。", "get_pdf_info"],
    [
        "Could you please explain how to browse YouTube on the car navigation system?",
        "get_pdf_info",
    ],
    ["カーナビのWebブラウザ機能を使ってYouTubeを視聴したいです。", "get_pdf_info"],
    [
        "I want to use the web browser feature on my car navigation system to watch YouTube.",
        "get_pdf_info",
    ],
    ["カーナビでYouTubeを見る手順を教えてください。", "get_pdf_info"],
    [
        "Can you provide instructions on how to watch YouTube on the car navigation system?",
        "get_pdf_info",
    ],
]

queries = [
    # ["カーナビのルートを設定したい", "get_pdf_lexus_info"],
    #    ["What is the procedure for watching YouTube on a car navigation system?", "get_pdf_lexus_info"],
    #    ['ビエラでハイブリッドキャストの設定の仕方を教えて', "get_pdf_viera_info"],
    ["How do I set up hybrid cast on my Viera?", "get_pdf_viera_info"],
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
