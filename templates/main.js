// main.js

function init_html() {
	const microphone = document.getElementById("microphone");
	microphone.style.backgroundImage = resources.microphoneImage;
}

document.addEventListener("DOMContentLoaded", function () {
	const networkHandler = new NetworkHandler();
	networkHandler.updateStatusHandler = updateStatus;

	const speechRecognitionHandler = new SpeechRecognitionHandler();
	speechRecognitionHandler.initializeRecognition(); //あとでこれ呼ばなくても良いように変更する
	speechRecognitionHandler.updateStatusHandler = updateStatus;
	let lang = 'ja-JP';

	init_html();
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
			// cCancel if the process is in progress.
			if (networkHandler.isProcessing || speechRecognitionHandler.isProcessing) {
				networkHandler.cancelAllConnections();
				speechRecognitionHandler.stopProcessing();
				return;
			}
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

	const microphone = document.getElementById('microphone');
	microphone.addEventListener('click', function () {
		// cCancel if the process is in progress.
		if (networkHandler.isProcessing || speechRecognitionHandler.isProcessing) {
			networkHandler.cancelAllConnections();
			speechRecognitionHandler.stopProcessing();
			return;
		}
		speechRecognitionHandler.startProcessing(lang);
	});

	const settingsButton = document.getElementById('settingImage');
	const overlay = document.getElementById('overlay');
	const modal = document.getElementById('modal');
	const saveButton = document.getElementById('saveButton');
	const cancelButton = document.getElementById('cancelButton');

	settingsButton.addEventListener('click', function () {
		overlay.style.display = 'block';
		modal.style.display = 'block';
	});

	saveButton.addEventListener('click', function () {
		const languageSelect = document.getElementById('language');
		const backgroundSelect = document.getElementById('background');

		const selectedLanguage = languageSelect.value;
		const selectedBackground = backgroundSelect.value;

		var videoElement = document.getElementById('video');
		videoElement.src = selectedBackground;
		videoElement.play();
		lang = selectedLanguage;

		updateStatus (`lang:${lang}`, 3);
		closeModal();
	});

	cancelButton.addEventListener('click', function () {
		closeModal();
	});

	function closeModal() {
		overlay.style.display = 'none';
		modal.style.display = 'none';
	}

	// Cancels processing other than speech recognition, network processing, voice playback processing, etc.
	speechRecognitionHandler.canceledHandler = function () {
		console.log('speechRecognitionHandler.cancelHandler');
		networkHandler.cancelAllConnections();
	}

	speechRecognitionHandler.recognizedHandler = function (text) {
		console.log('speechRecognitionHandler.recognizedHandler ');
		networkHandler.setupEventSource(text, lang);
	}


});
