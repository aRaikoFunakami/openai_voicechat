# original site of video
# https://commons.wikimedia.org/wiki/File:Big_Buck_Bunny_4K.webm
# https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c0/Big_Buck_Bunny_4K.webm/Big_Buck_Bunny_4K.webm.720p.webm
from flask import Flask, render_template, request, Response
import flask
import queue
import logging
import openai_chat
import threading
import requests

# フリー素材: https://icooon-mono.com/
app = Flask(__name__, static_folder="./templates", static_url_path="")


@app.route("/audio_query", methods=["GET", "POST"])
def audio_query():
    # リクエストの情報を取得
    url = "http://127.0.0.1:50021/audio_query"  # リレー先のURL

    method = request.method  # リレーするHTTPメソッド
    # headers = request.headers  # オリジナルのリクエストヘッダー
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = request.data  # オリジナルのリクエストボディ
    # リクエストをリレーする
    # for i, j in request.args.items():
    #    print(f'args: {i}, {j}')
    response = requests.request(
        method, url, headers=headers, data=data, params=request.args
    )
    # print(f'audio_query: method:{method}, headers:{headers}, params:{request.args}, data:{data}, response: {response}')
    # レスポンスを返す
    return response.text, response.status_code, response.headers.items()


@app.route("/synthesis", methods=["GET", "POST"])
def synthesis():
    # リクエストの情報を取得
    url = "http://127.0.0.1:50021/synthesis"  # リレー先のURL
    method = request.method  # リレーするHTTPメソッド
    headers = {"Content-Type": "application/json"}
    data = request.json  # オリジナルのリクエストボディ（JSON形式）
    # リクエストをリレーする
    response = requests.request(
        method, url, headers=headers, json=data, params=request.args
    )
    # print(f'synthesis: method:{method}, headers:{headers}, params:{request.args}, data:{data}, response: {response}')
    # print(f'synthesis: response: {response.text}')
    # レスポンスを返す
    # バイナリデータを含むレスポンスを作成する
    relay_response = Response(
        response.content, status=response.status_code, headers=dict(response.headers)
    )

    return relay_response


import langchain_agent


@app.route("/input", methods=["GET"])
def input():
    logging.info(request)
    input = request.args["text"]
    function = request.args.get("function")
    print(f"function: {function}")
    qa_stream = queue.Queue()

    def dummy_callback(response=None):
        qa_stream.put(response)
        # if response is not None:
        #    logging.info("response:%s",response)

    # callbackの処理を並行して動かすので別スレッドで ChatGPT に問い合わせる
    # producer_thread = threading.Thread(target=openai_chat.chat, args=(input,dummy_callback))
    # LEXUS のマニュアルについて回答する
    # producer_thread = threading.Thread(target=openai_chatPDF.chat, args=(input,dummy_callback))
    # producer_thread.start()

    producer_thread = threading.Thread(
        target=langchain_agent.chat, args=(input, dummy_callback, function)
    )
    producer_thread.start()

    #
    def stream():
        while True:
            msg = qa_stream.get()
            # print(msg)
            if msg is None:
                break
            yield f"data: {msg}\n\n"

    stream_res = flask.Response(stream(), mimetype="text/event-stream")
    return stream_res


@app.route("/")
def index():
    return render_template("index.html")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s:%(filename)s:%(funcName)s - %(message)s",
)
app.run(host="0.0.0.0", port=8080, debug=True)
# app.run(host='0.0.0.0', port=8001, debug=True, ssl_context=('openssl/server.crt', 'openssl/server.key'))
# app.run(host='0.0.0.0', port=443, debug=True, ssl_context=('openssl/server.crt', 'openssl/server.key'))
