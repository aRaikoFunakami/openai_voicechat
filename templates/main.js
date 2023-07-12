// main.js

function init_html() {
	const microphone = document.getElementById("microphone");
	microphone.style.backgroundImage = resources.microphoneImage;

	const videoElement = document.getElementById('video');
	const newSource = resources.videoUrls[0];
	videoElement.setAttribute('src', newSource);

	const settingImageElement = document.getElementById('settingImage');
	const settingImageSrc = resources.settingImage;
	settingImageElement.setAttribute('src', settingImageSrc);

	//const characterImageElement = document.getElementById('characterImage');
	//const characterImageSrc = resources.zunmonImage;
	//characterImageElement.setAttribute('src', characterImageSrc);

	const backgroundSelect = document.getElementById('background');
	for (var i = 0; i < resources.videoUrls.length; i++) {
		var option = document.createElement('option');
		option.value = resources.videoUrls[i];
		option.text = 'Background ' + (i + 1);
		backgroundSelect.appendChild(option);
	}
}

document.addEventListener("DOMContentLoaded", function () {
	const networkHandler = new NetworkHandler();
	networkHandler.updateStatusHandler = updateStatus;
	networkHandler.updateAnswerHandler = updateAnswer;
	networkHandler.speechEndHandler = updateAnswer;

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

	// answer area
	function updateAnswer(text, isStop) {
		const answerElement = document.getElementById('answer');
		const answertextElement = document.getElementById('answer_text');
		console.log(`updateAnswer ${text}, ${isStop}`)
		if(isStop){
			answertextElement.innerHTML = '';
			answerElement.style.display = "none";
		}else{
			answertextElement.innerHTML = marked.parse(answertextElement.innerText + text);
			answertextElement.scrollTop = answertextElement.scrollHeight;
			answerElement.style.display = "flex";
		}
	}

	//
	// same as e.code === 'Space'
	//
	const microphone = document.getElementById('microphone');
	microphone.addEventListener('click', function () {
		// cCancel if the process is in progress.
		if (networkHandler.isProcessing || speechRecognitionHandler.isProcessing) {
			networkHandler.cancelAllConnections();
			speechRecognitionHandler.stopProcessing();
			updateAnswer('', true);
			return;
		}
		speechRecognitionHandler.startProcessing(lang);
	});

	//
	// Setting by Keys
	//
	let videoTimes = new Array(resources.videoUrls.length).fill(0);
	let currentVideoIndex = 0;
	// background
	window.addEventListener('keypress', function (event) {
		if (event.keyCode >= 49 && event.keyCode <= 57) {
			var videoIndex = event.keyCode - 49; // 49 is the keyCode for '1'
			if (resources.videoUrls[videoIndex] !== undefined) {
				var videoElement = document.getElementById('video');
				videoTimes[currentVideoIndex] = videoElement.currentTime;
				videoElement.src = resources.videoUrls[videoIndex];
				videoElement.currentTime = videoTimes[videoIndex];
				videoElement.play();
				currentVideoIndex = videoIndex;
			}
		}
	});
	// language
	window.addEventListener('keypress', (e) => {
		if (e.code === 'Space') {
			// cCancel if the process is in progress.
			if (networkHandler.isProcessing || speechRecognitionHandler.isProcessing) {
				networkHandler.cancelAllConnections();
				speechRecognitionHandler.stopProcessing();
				updateAnswer('', true);
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

	//
	// Setting Dialog
	//
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
		// background
		let videoIndex = backgroundSelect.selectedIndex - 1;
		if (resources.videoUrls[videoIndex] !== undefined) {
			var videoElement = document.getElementById('video');
			videoTimes[currentVideoIndex] = videoElement.currentTime;
			videoElement.src = selectedBackground
			videoElement.currentTime = videoTimes[videoIndex];
			videoElement.play();
			currentVideoIndex = videoIndex;
		}
		// language
		lang = selectedLanguage;
		updateStatus(`lang:${lang}`, 3);
		closeModal();
	});

	cancelButton.addEventListener('click', function () {
		closeModal();
	});

	function closeModal() {
		overlay.style.display = 'none';
		modal.style.display = 'none';
	}

	//
	// Handers
	//

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


