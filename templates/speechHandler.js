// speechHandler.js

function splitTextByDelimiters(text, delimiters) {
	let index = text.length;

	for (const delimiter of delimiters) {
		const delimiterIndex = text.indexOf(delimiter);
		if (delimiterIndex !== -1 && delimiterIndex < index) {
			index = delimiterIndex;
		}
	}

	let firstPart = '';
	let restPart = '';

	if (index !== -1) {
		firstPart = text.slice(0, index + 1);
		restPart = text.slice(index + 1);
		for (const delimiter of delimiters) {
			firstPart = firstPart.replace(delimiter, ' ');
		}
	} else {
		firstPart = text;
	}

	return [firstPart, restPart];
}



class SpeechHandler {
	constructor() {
		this.utterances = [];
		this.text = "";
		this.delimiters = [',', '.', '!', ':', ';', '?', '{', '}', '[', ']', '！', '？', '：', '；', '　', '。', '、',];
	}

	handleSpeechEnd(event) {
		const utterance = event.target;
		const isStop = utterance.isStop;
		console.log(`utterance.finish: ${isStop}`);
	}

	speakUtterance(text, isStop, lang) {
		const utterance = new SpeechSynthesisUtterance(text);
		utterance.isStop = isStop;
		utterance.onend = this.handleSpeechEnd.bind(this);
		//
		// Ugh!: hard coding...
		// language setting before speak
		//
		console.log(`SpeechHandler.speakUtterance ${lang}`)
		var voices = speechSynthesis.getVoices()
		if (lang == 'en-US') {
			utterance.lang = 'en-US';
			//utterThis.voice = voices[39]; // en-US:Fred
			utterance.voice = voices[145]; // en-US:Google US English Female
			//utterThis.voice = voices[146]; // en-GB:Google UK English Female
			utterance.rate = 0.9;
		} else if (lang == 'zh-CN') {
			utterance.lang = 'zh-CN';
			utterance.voice = voices[169]; // zh-CN: Google 普通話
			utterance.rate = 0.9;
		}
		this.utterances.push(utterance);
		speechSynthesis.speak(utterance);
	}

	speak(text, isStop, lang) {
		this.text += text + ' ';
		while (true) {
			const [firstPart, restPart] = splitTextByDelimiters(this.text, this.delimiters);
			//console.log(`firstPart:${firstPart}, restPart:${restPart}(${restPart == ""}})`);

			// Buffer is empty, but speak is called again
			if (restPart == "" && isStop != true) {
				break;
			}

			// If there is still data to read, call isStop with false
			if (restPart != "") {
				this.speakUtterance(firstPart, false, lang);
			} else {
				this.speakUtterance(firstPart, isStop, lang);
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
		this.utterances.forEach((utterance) => {
			console.log(`Cancel audio output: ${utterance.text}`);
			speechSynthesis.cancel();
		});
	}
}
