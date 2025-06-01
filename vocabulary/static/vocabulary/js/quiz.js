// 퀴즈 관련 전역 변수
let timeLeft = 60;
let currentWord = 1;
let totalWords = 0;

// DOM 요소
const timerElement = document.getElementById('time');
const progressBar = document.getElementById('progress-bar');
const quizForm = document.getElementById('quiz-form');

// 타이머 업데이트 함수
function updateTimer() {
    timeLeft--;
    if (timerElement) {
        timerElement.textContent = timeLeft;
    }
    if (progressBar) {
        progressBar.style.width = (timeLeft / 60 * 100) + '%';
    }
    
    if (timeLeft <= 0) {
        clearInterval(timer);
        if (quizForm) {
            quizForm.submit();
        }
    }
}

// 단어 발음 함수
function speakWord(word) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        speechSynthesis.speak(utterance);
    } else {
        alert('이 브라우저는 음성 합성을 지원하지 않습니다.');
    }
}

// 단어 카드 표시 함수
function showWord(index) {
    const wordCards = document.querySelectorAll('.word-card');
    wordCards.forEach(card => card.style.display = 'none');
    const currentCard = document.getElementById('word-' + index);
    if (currentCard) {
        currentCard.style.display = 'block';
    }
}

// 다음 단어로 이동
function nextWord() {
    if (currentWord < totalWords) {
        currentWord++;
        showWord(currentWord);
    }
}

// 이전 단어로 이동
function previousWord() {
    if (currentWord > 1) {
        currentWord--;
        showWord(currentWord);
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 타이머 시작
    const timer = setInterval(updateTimer, 1000);
    
    // 첫 번째 단어 표시
    showWord(1);
    
    // 키보드 이벤트 리스너
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowRight') {
            nextWord();
        } else if (e.key === 'ArrowLeft') {
            previousWord();
        }
    });
}); 