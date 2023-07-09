

class SpeechHandlerZundamon {
	constructor() {
		this.player = new VoiceVoxPlayer();
		this.player.audioEndedHandler = this.handleSpeechEnd;
		this.abortController = new AbortController();
		this.text = "";
		this.delimiters = [',', '.', '!', ':', ';', '?', '{', '}', '[', ']', '！', '？', '：', '；', '　', '。', '、',];
	}

	handleSpeechEnd(e) {
		console.log(`handleSpeechEnd: [${e.isStop}] ${e.text}`);
	}

	speak(text, isStop, lang) {
		console.log(`SpeechHandlerZundamon.speak ${text}, ${isStop}, (${this.player}, ${this.abortController})`)
		this.text += text + ' ';
		while (true) {
			const [firstPart, restPart] = splitTextByDelimiters(this.text, this.delimiters);
			// console.log(`firstPart:${firstPart}, restPart:${restPart}(${restPart == ""}})`);

			// Buffer is empty, but speak is called again
			if (restPart == "" && isStop != true) {
				break;
			}

			// If there is still data to read, call isStop with false
			if (restPart != "") {
				this.player.playAudio(firstPart, false);
			} else {
				this.player.playAudio(firstPart, isStop);
			}

			// If there is data left to read, repeat again.
			this.text = restPart;
			if (this.text != "") {
				continue;
			}
			break;
		}
	}

	cancelAllSpeeches() {
		this.player.abort();
	}
}
