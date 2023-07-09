// main.js

document.addEventListener("DOMContentLoaded", function () {
	const myButton = document.getElementById("myButton");
	const cancelButton = document.getElementById("cancelButton");
	const networkHandler = new NetworkHandler();
	const speechRecognitionHandler = new SpeechRecognitionHandler();
	speechRecognitionHandler.initializeRecognition(); //あとでこれ呼ばなくても良いように変更する
	speechRecognitionHandler.updateStatusHandler = updateStatus;
	let lang = 'ja-JP';

	myButton.addEventListener("click", function () {
		networkHandler.setupEventSource('横浜の天気 晴天', lang);
	});

	cancelButton.addEventListener("click", function () {
		networkHandler.cancelAllConnections();
	});

	// status display area (notification and debug)
	let timeoutHandle_updateStatus = null;
	function updateStatus(text, displayTime = 1) {
		const statusElement = document.getElementById('status');

		clearTimeout(timeoutHandle_updateStatus); // 前回の非表示処理をキャンセル
		statusElement.textContent = text;
		statusElement.style.display = "block";

		timeoutHandle_updateStatus = setTimeout(function () {
			statusElement.style.display = "none";
		}, displayTime * 1000);
	}

	// change language
	window.addEventListener('keypress', (e) => {
		if (e.code === 'Space') {
			speechRecognitionHandler.startProcessing(lang);
		}
		else if (e.code === 'KeyE') {
			lang = 'en-US';
			updateStatus('Language:' + lang, 2);
		}
		else if (e.code === 'KeyJ') {
			lang = 'ja-JP';
			updateStatus('Language:' + lang, 2);
		}
		else if (e.code === 'KeyZ') {
			// https://segakuin.com/html/attribute/lang.html
			lang = 'zh-CN';
			updateStatus('Language:' + lang, 2);
		}
	});

	// Cancels processing other than speech recognition, network processing, voice playback processing, etc.
	speechRecognitionHandler.canceledHandler = function(){
		console.log('speechRecognitionHandler.cancelHandler');
		networkHandler.cancelAllConnections();
	}

	speechRecognitionHandler.recognizedHandler = function(text){
		console.log('speechRecognitionHandler.recognizedHandler ');
		networkHandler.setupEventSource(text, lang);
	}
});
