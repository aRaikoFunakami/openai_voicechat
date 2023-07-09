// networkHandler.js

class NetworkHandler {
	constructor() {
		this.eventSources = [];
		this.speechHandler = new SpeechHandler();
		//this.speechHandler = new SpeechHandlerZundamon();
		this.lang = null;
	}

	cancelAllConnections() {
		this.eventSources.forEach((eventSource) => {
			if (eventSource && eventSource.readyState !== EventSource.CLOSED) {
				console.log(`Cancel network connection: ${eventSource.url}`);
				eventSource.close();
			}
		});
		this.speechHandler.cancelAllSpeeches();
	}

	handleEventSourceMessage(event) {
		const jsonData = JSON.parse(event.data);
		const text = jsonData.response;
		const type = jsonData.type;
		const finish = jsonData.finish_reason;
		console.log(`NetworkHandler.handleEventSourceMessage text: ${text}, type: ${type}, finish: ${finish}`);
		this.speechHandler.speak(text, finish === "stop", this.lang);
	}

	setupEventSource(text, lang = 'ja-JP') {
		this.lang = lang;
		const eventSource = new EventSource(`http://127.0.0.1:8001/input?text=${encodeURIComponent(text)}`);
		this.eventSources.push(eventSource);
		eventSource.onmessage = this.handleEventSourceMessage.bind(this);
	}
}
