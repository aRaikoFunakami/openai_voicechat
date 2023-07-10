const server = 'http://127.0.0.1:8001';
const voicevoxserver = 'http://127.0.0.1:50021';

const resources = {
	server: `${server}`,
	audioQueryUrl: `${voicevoxserver}/audio_query?speaker=1`,
	synthesisUrl: `${voicevoxserver}/synthesis?speaker=1`,
	// for CSS
	microphoneImage: `url(${server}/media/icon_mic.png)`,
	// for JS
	settingImage: `${server}/media/icon_setting.png`,
	zunmonImage: `${server}/media/zunmon.png`,
	videoUrls: [
		`${server}/media/background_carnavi.mp4`,
		`${server}/media/background_lexus_navi.mp4`,
		`${server}/media/background_bigbuckbunny.webm`,
		`${server}/media/background_soccer.mp4`,
		//... more URLs if needed
	],
	// 他のリソースもここに追加できます
};

// フリー素材
// https://icooon-mono.com/00001-%E7%84%A1%E6%96%99%E3%81%AE%E8%A8%AD%E5%AE%9A%E6%AD%AF%E8%BB%8A%E3%82%A2%E3%82%A4%E3%82%B3%E3%83%B3/
