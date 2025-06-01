// 음성 합성 관련 클래스
class SpeechManager {
    constructor() {
        this.synthesis = window.speechSynthesis;
        this.voices = [];
        this.selectedVoice = null;
        this.rate = 1.0;
        this.pitch = 1.0;
        this.volume = 1.0;
        
        this.init();
    }
    
    // 초기화
    init() {
        if (!this.synthesis) {
            console.error('이 브라우저는 음성 합성을 지원하지 않습니다.');
            return;
        }
        
        // 음성 목록 로드
        this.loadVoices();
        
        // 음성 목록이 변경될 때 이벤트 처리
        this.synthesis.onvoiceschanged = () => this.loadVoices();
    }
    
    // 음성 목록 로드
    loadVoices() {
        this.voices = this.synthesis.getVoices();
        // 영어 음성 찾기
        this.selectedVoice = this.voices.find(voice => 
            voice.lang.includes('en') && voice.name.includes('Female')
        ) || this.voices.find(voice => 
            voice.lang.includes('en')
        ) || this.voices[0];
    }
    
    // 단어 발음
    speak(word) {
        if (!this.synthesis || !this.selectedVoice) {
            alert('이 브라우저는 음성 합성을 지원하지 않습니다.');
            return;
        }
        
        // 이전 발음 중지
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.voice = this.selectedVoice;
        utterance.rate = this.rate;
        utterance.pitch = this.pitch;
        utterance.volume = this.volume;
        
        this.synthesis.speak(utterance);
    }
    
    // 발음 중지
    stop() {
        if (this.synthesis) {
            this.synthesis.cancel();
        }
    }
    
    // 속도 설정
    setRate(rate) {
        this.rate = rate;
    }
    
    // 음높이 설정
    setPitch(pitch) {
        this.pitch = pitch;
    }
    
    // 볼륨 설정
    setVolume(volume) {
        this.volume = volume;
    }
}

// 전역 인스턴스 생성
const speechManager = new SpeechManager();

// 단어 발음 함수 (전역 스코프)
function speakWord(word) {
    speechManager.speak(word);
} 