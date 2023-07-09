// networkHandler.js

class NetworkHandler {
	constructor() {
		this.eventSources = [];
		this.speechHandler = new SpeechHandler();
		this.speechHandlerZundamon = new SpeechHandlerZundamon();
		this.lang = null;
	}

	cancelAllConnections() {
		console.log('NetworkHandler.cancelAllConnections');
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
		if(this.lang == 'ja-JP'){
			this.speechHandlerZundamon.speak(text, finish === "stop", this.lang);
		}
		else{
			this.speechHandler.speak(text, finish === "stop", this.lang);
		}
	}

	handleEventSourceError(event) {
		console.error('Error occurred:', event);
		this.eventSources.forEach((source)=>{
			source.close();
		});
	}

	setupEventSource(text, lang = 'ja-JP') {
		this.lang = lang;
		const eventSource = new EventSource(`http://127.0.0.1:8001/input?text=${encodeURIComponent(text)}`);
		this.eventSources.push(eventSource);
		eventSource.onmessage = this.handleEventSourceMessage.bind(this);
		eventSource.onerror = this.handleEventSourceError.bind(this);
	}
}
