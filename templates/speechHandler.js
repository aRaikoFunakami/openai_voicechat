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
		this.delimitersDefault = ['\t', '\n', '!', ':', ';', '?', '{', '}', '[', ']', '！', '？', '：', '；', '　', '。', '、',];
		this.delimitersJa = ['「', '」', '！', '？', '：', '；', '　', '。', '、',];
		this.delimiters = this.delimitersDefault;

		// Handler
		this.speechEndHandler = null;

		// Chrome will return an empty array if the first call is to an empty array.
		speechSynthesis.getVoices();
	}

	handleSpeechEnd(event) {
		const utterance = event.target;
		const text = utterance.text;
		const isStop = utterance.isStop;
		console.log(`utterance.finish: ${text}, ${isStop}`);

		this.speechEndHandler(isStop);
	}

	speakUtterance(text, isStop, lang) {
		const utterance = new SpeechSynthesisUtterance(text);
		utterance.isStop = isStop;
		utterance.onend = this.handleSpeechEnd.bind(this);
		//
		// Ugh!: hard coding...
		// language setting before speak
		// https://ao-system.net/pwa/speak/
		//
		console.log(`SpeechHandler.speakUtterance ${lang}`)
		var voices = speechSynthesis.getVoices();

		utterance.lang = lang;
		if (lang == 'en-US') {
			utterance.voice = voices[145]; // en-US:Google US English Female
			utterance.rate = 0.9;
			this.delimiter = this.delimitersDefault;
		} else if (lang == 'zh-CN') {
			utterance.voice = voices[169]; // zh-CN: Google 普通話
			utterance.rate = 0.9;
			this.delimiters = this.delimitersDefault;
		} else if (lang == 'ko-KR') {
			utterance.voice = voices[155];
			utterance.rate = 1.0;
			this.delimiters = this.delimitersDefault;
		} else if (lang == 'ja-JP') {
			this.delimiters = this.delimitersJa;
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
			console.log(`speak this.speakUtterance firstPart:${firstPart}, restPart: ${restPart}, this.text = ${this.text}`);

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
