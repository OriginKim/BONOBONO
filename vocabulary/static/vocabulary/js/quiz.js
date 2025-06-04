// 퀴즈 관련 전역 변수
let timeLeft = parseInt(document.getElementById('time').textContent);
let currentWord = 1;
let totalWords = document.querySelectorAll('.word-card').length;
let timer = null;

// DOM 요소
const timerElement = document.getElementById('time');
const progressBar = document.getElementById('progress-bar');
const quizForm = document.getElementById('quiz-form');

// 타이머 업데이트 함수
function updateTimer() {
    timeLeft--;
    
    // 타이머 텍스트 업데이트
    if (timerElement) {
        timerElement.textContent = timeLeft;
    }
    
    // 프로그레스바 업데이트
    if (progressBar) {
        const totalTime = parseInt(document.getElementById('time').textContent);
        const progress = (timeLeft / totalTime) * 100;
        progressBar.style.width = `${progress}%`;
        
        // 프로그레스바 색상 업데이트
        if (timeLeft <= totalTime * 0.2) {  // 20% 이하
            progressBar.className = 'progress-bar bg-danger';
        } else if (timeLeft <= totalTime * 0.5) {  // 50% 이하
            progressBar.className = 'progress-bar bg-warning';
        } else {
            progressBar.className = 'progress-bar bg-success';
        }
    }
    
    // 시간 종료 체크
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
    const navButtons = document.querySelectorAll('.word-number-btn');
    
    // 모든 카드 숨기기
    wordCards.forEach(card => card.classList.remove('active'));
    
    // 모든 네비게이션 버튼에서 current 클래스 제거
    navButtons.forEach(btn => btn.classList.remove('current'));
    
    // 현재 카드와 네비게이션 버튼 활성화
    const currentCard = document.getElementById(`word-${index}`);
    const currentNav = document.getElementById(`nav-${index}`);
    
    if (currentCard) {
        currentCard.classList.add('active');
    }
    if (currentNav) {
        currentNav.classList.add('current');
    }
    
    currentWord = index;
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

// 특정 단어로 이동
function goToWord(index) {
    if (index >= 1 && index <= totalWords) {
        showWord(index);
    }
}

// 답변 표시 함수
function markAsAnswered(index) {
    const navBtn = document.getElementById(`nav-${index}`);
    if (navBtn) {
        navBtn.classList.add('answered');
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 타이머 시작
    timer = setInterval(updateTimer, 1000);
    
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