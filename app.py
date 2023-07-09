# original site of video
# https://commons.wikimedia.org/wiki/File:Big_Buck_Bunny_4K.webm
# https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c0/Big_Buck_Bunny_4K.webm/Big_Buck_Bunny_4K.webm.720p.webm
from flask import Flask, render_template, request
import flask
import queue
import logging
import threading
import time
import json

app = Flask(__name__, static_folder='./templates', static_url_path='')

texts = [
    #"In JavaScript, arrays can be accessed using square brackets [], and objects can be defined using curly braces {}.",
    #"新しい日が明け、 風は爽やかに吹く。 人々は笑顔で歩き、 夢を追いかける！",
    #"新的一天开始了，微风轻拂。人们笑容满面，追逐梦想！",
]

def dummy_chatGPT(callback, response = None):
    if(response is None):
        joined_text = ' '.join(texts)
    else:
        joined_text = ' '.join(response)

    words = joined_text.split()
    print(words)

    index = 0
    for i in words:
        message = {'response': i, 'type': None, 'finish_reason': None}
        callback(json.dumps(message))
        index = index + 1
        if index % 4 == 0:
            time.sleep(1)

    message = {'response': '', 'type': None, 'finish_reason': 'stop'}
    callback(json.dumps(message))
    return

@app.route('/input', methods=["GET"])
def input():
    logging.info(request)
    input = request.args['text']
    dummy_response = []
    dummy_response.append(input)
    qa_stream = queue.Queue()
    def dummy_callback(response=None):
        qa_stream.put(response)

    producer_thread = threading.Thread(target=dummy_chatGPT, args=(dummy_callback, dummy_response, ))
    producer_thread.start()

    def stream():
        while True:
            msg = qa_stream.get()
            if msg is None:
                break
            yield f'data: {msg}\n\n'

    stream_res = flask.Response(stream(), mimetype='text/event-stream')
    return stream_res

@app.route('/')
def index():
    return render_template('index.html')

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(filename)s:%(funcName)s - %(message)s")
app.run(port=8001, debug=True)
