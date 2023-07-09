class VoiceVoxPlayer {
	constructor() {
		this.audioPlayQueue = Promise.resolve();
		this.audioGenerationQueue = [];
		this.audioEndedHandler = null;
		this.abortController = null;
	}

	playAudio(
		textData,
		isStop,
		audioQueryUrl = "http://127.0.0.1:50021/audio_query?speaker=1",
		synthesisUrl = "http://127.0.0.1:50021/synthesis?speaker=1"
	) {
		var audioQueryData = "&text=" + encodeURIComponent(textData);
		audioQueryUrl = audioQueryUrl + audioQueryData;

		let abortController = new AbortController();
		let audioGeneration = fetch(audioQueryUrl, {
			method: "POST",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded"
			},
			body: "",
			signal: abortController.signal
		})
			.then(response => response.json())
			.then(data => {
				var jsonData = JSON.stringify(data);

				return fetch(synthesisUrl, {
					method: "POST",
					headers: {
						"Content-Type": "application/json"
					},
					body: jsonData,
					signal: abortController.signal
				});
			})
			.then(response => response.blob())
			.then(blob => {
				var audio = new Audio();
				audio.src = URL.createObjectURL(blob);
				return [audio, abortController];
			})
			.catch(error => {
				console.error("voice generation error:", error);
				throw error;
			});
		this.audioGenerationQueue.push([audioGeneration, textData, isStop, abortController]);
		this.processAudioQueue();
	}

	processAudioQueue() {
		this.audioPlayQueue = this.audioPlayQueue
			.then(() => {
				let nextTask = this.audioGenerationQueue.shift();
				if (!nextTask) {
					return Promise.resolve();
				}
				let [nextAudioPromise, textData, isStop, abortController] = nextTask;
				this.abortController = abortController;

				return nextAudioPromise.then(([audio]) =>
					new Promise((resolve, reject) => {
						const handleAbort = () => {
							audio.pause();
							audio.src = "";
							audio.removeEventListener("ended", handleEnded);
							URL.revokeObjectURL(audio.src);
							reject(new DOMException("Audio playback aborted", "AbortError"));
						};

						this.abortController.signal.addEventListener("abort", handleAbort);

						const handleEnded = () => {
							this.abortController.signal.removeEventListener("abort", handleAbort);
							console.log(`audio.onended ${this.audioEndedHandler}, ${textData}`);
							if (this.audioGenerationQueue.length === 0) {
								const e = {
									text: textData
								};
								if (this.audioEndedHandler) {
									this.audioEndedHandler(e);
								}
							}
							resolve();
						};

						audio.addEventListener("ended", handleEnded);

						audio.play().catch(reject);
					})
				);
			})
			.catch(error => {
				console.error("playback error:", error);
				throw error;
			});
	}

	abort() {
		if (this.abortController) {
			this.abortController.abort();
		}
		for (let task of this.audioGenerationQueue) {
			let [audioGeneration, textData, isStop, abortController] = task;
			abortController.abort();
		}
		this.audioGenerationQueue = [];
		this.audioPlayQueue = Promise.resolve();
		this.abortController = null;
	}
}
