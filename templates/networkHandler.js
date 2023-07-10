// networkHandler.js

class NetworkHandler {
	constructor() {
		this.isProcessing = false;
		this.eventSources = [];
		this.speechHandler = new SpeechHandler();
		this.speechHandlerZundamon = new SpeechHandlerZundamon();
		this.lang = null;

		//handlers
		this.updateStatusHandler = null;
		this.updateAnswerHandler = null;
		this.speechEndHandler = null;
	}

	cancelAllConnections() {
		console.log('NetworkHandler.cancelAllConnections');
		this.isProcessing =  false;

		this.eventSources.forEach((eventSource) => {
			if (eventSource && eventSource.readyState !== EventSource.CLOSED) {
				console.log(`Cancel network connection: ${eventSource.url}`);
				eventSource.close();
			}
		});
		this.speechHandler.cancelAllSpeeches();
		this.speechHandlerZundamon.cancelAllSpeeches();
	}

	handleEventSourceMessage(event) {
		const jsonData = JSON.parse(event.data);
		const text = jsonData.response;
		const type = jsonData.type;
		const finish = jsonData.finish_reason;
		console.log(`NetworkHandler.handleEventSourceMessage text: ${text}, type: ${type}, finish: ${finish}`);

		if (type == 'notification') {
			//status.innerText = text;
			this.updateStatusHandler(text, 1);
			return;
		}
		this.updateAnswerHandler(text, false);
		//else {
		// ストリームで受け取ったデータを徐々に表示する
		//answer.style.display = 'flex';
		//answer_text.innerHTML = answer_text.innerHTML + data;
		//}
		// レスポンス領域を自動スクロール
		//answer_text.scrollTop = answer_text.scrollHeight;

		if (this.lang == 'ja-JP') {
			this.speechHandlerZundamon.speak(text, finish === "stop", this.lang);
			this.speechHandlerZundamon.speechEndHandler = function(isStop) {
				this.isProcessing = !isStop;
				this.speechEndHandler('', isStop);
			}.bind(this);
		}
		else {
			this.speechHandler.speak(text, finish === "stop", this.lang);
			this.speechHandler.speechEndHandler = function(isStop) {
				this.isProcessing = !isStop;
				this.speechEndHandler('', isStop);
			}.bind(this);
		}


	}

	handleEventSourceError(event) {
		console.error('Error occurred:', event);
		this.eventSources.forEach((source) => {
			source.close();
		});
	}

	setupEventSource(text, lang = 'ja-JP') {
		this.isProcessing = true;
		this.lang = lang;
		const eventSource = new EventSource(`${resources.server}/input?text=${encodeURIComponent(text)}`);
		this.eventSources.push(eventSource);
		eventSource.onmessage = this.handleEventSourceMessage.bind(this);
		eventSource.onerror = this.handleEventSourceError.bind(this);
	}
}
