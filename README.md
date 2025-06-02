# BONOBONO 영어 단어 학습 시스템

## 프로젝트 개요
BONOBONO는 Django 기반의 영어 단어 학습 시스템으로, C로 구현한 자료구조(큐, 스택, 원형 연결 리스트)를 Python(ctypes)으로 연동하여 실제 서비스의 핵심 기능에 적극적으로 활용합니다.

---

## 기술 스택 및 구조

### 백엔드
- **Python 3, Django** : 웹 서버, API, 인증, 세션 관리 등
- **C (자료구조 엔진)** : 큐, 스택, 원형 연결 리스트 등 핵심 자료구조를 고성능 C로 직접 구현
- **ctypes** : Python에서 C 라이브러리 함수 직접 호출 및 구조체 연동

### 데이터베이스
- **MySQLWorkbench (Django ORM)** : 사용자, 단어, 퀴즈, 오답노트 등 영구 데이터 저장

### 프론트엔드
- **HTML/CSS (Django 템플릿)** : 사용자별 맞춤 페이지, 퀴즈/오답 복습 UI
- **JavaScript (fetch API)** : 오답 복습 등에서 비동기 API 호출 및 동적 페이지 전환

---

## 주요 기능과 자료구조/엔진 연동

### 1. 퀴즈 생성/응시 (큐 활용)
- 선생님이 퀴즈를 생성하면, 선택한 단어들이 **C로 구현된 큐**에 enqueue됨
- 학생이 퀴즈를 풀 때, 큐에서 dequeue하여 문제를 출제
- **API/뷰**: `create_quiz`, `take_quiz` (views.py)
- **C 함수**: `createQueue`, `enqueue`, `dequeue`
- **연동 방식**: Python에서 ctypes로 C 함수 호출, 단어 구조체 변환

### 2. 오답노트 (DB/ORM)
- 학생별로 최근에 틀린 단어, 틀린 횟수, 마지막 틀린 날짜를 DB(`WrongWord` 모델)에 저장
- **자료구조 엔진 사용 X** (Django ORM 쿼리만 사용)
- **API/뷰**: `wrong_words` (views.py)

### 3. 오답 복습 (스택 + 원형 연결 리스트 활용)
- 오답노트의 단어를 **스택(C)**에 push → pop해서 **원형 연결 리스트(C)**에 insert
- 원형 리스트를 순환하며 오답 복습(이전/다음, 반복)
- **API/뷰**: `review_wrong_words`, `api_next_wrong_word`, `api_prev_wrong_word` (views.py)
- **C 함수**: `initStack`, `push`, `pop`, `createCircularList`, `insertWord`, `moveToNext`, `moveToPrevious`, `getCurrentWord`, `getCurrentIndex`
- **연동 방식**: Python에서 C 구조체 포인터를 세션에 저장/복원, JS fetch로 API 호출
- **실제 응용**: 오답 복습 시 단어 순환, 인덱스(몇 번째 단어인지)도 C에서 직접 계산하여 정확히 표시

### 4. 암기법 생성 (LLM API)
- OpenAI API를 활용해 단어별 연상 암기법 자동 생성
- **API/뷰**: `generate_association` (views.py)
- **연동 방식**: JS fetch로 프론트엔드에서 호출, 백엔드에서 OpenAI API 연동

---

## 자료구조별 상세 설명 및 응용 사례

### 큐(Queue)
- **C로 구현**: 단어를 순서대로 저장/출제
- **Python 연동**: ctypes로 C 함수 호출
- **실제 활용**: 퀴즈 출제/응시 시 단어 순서 보장

### 스택(Stack)
- **C로 구현**: 오답 단어를 LIFO로 저장
- **Python 연동**: ctypes로 C 함수 호출
- **실제 활용**: 오답 복습용 단어 임시 저장, pop 순서대로 원형 리스트에 삽입

### 원형 연결 리스트(Circular List)
- **C로 구현**: 오답 복습용 단어를 원형 구조로 저장, 순환 학습 지원
- **Python 연동**: ctypes로 C 함수 호출, 구조체 포인터 세션 저장/복원
- **실제 활용**: 오답 복습(이전/다음, 반복), 인덱스 계산(getCurrentIndex)로 현재 위치 정확히 표시

---

## API/뷰 요약

| 기능                | 자료구조         | 주요 API/뷰 함수                | C 함수/구조체                |
|---------------------|------------------|-------------------------------|------------------------------|
| 퀴즈 생성/응시      | 큐               | create_quiz, take_quiz        | createQueue, enqueue, dequeue|
| 오답노트            | (DB)             | wrong_words                   | (X)                          |
| 오답 복습           | 스택, 원형리스트 | review_wrong_words, api_next_wrong_word, api_prev_wrong_word | initStack, push, pop, createCircularList, insertWord, moveToNext, moveToPrevious, getCurrentWord, getCurrentIndex |
| 암기법 생성         | (X)              | generate_association          | (OpenAI API)                 |

---

## 실제 연동 구조

1. **C로 자료구조 엔진 구현**
   - 각 자료구조별 함수/구조체를 C로 작성, 빌드하여 .so 라이브러리 생성
2. **Python(ctypes)에서 C 함수 등록**
   - c_library.py에서 각 함수/구조체를 ctypes로 등록, Python에서 직접 호출
3. **Django 뷰에서 자료구조 활용**
   - 퀴즈/오답 복습 등에서 C 자료구조를 실시간으로 생성/조작
   - 구조체 포인터를 세션에 저장/복원하여 사용자별 상태 유지
4. **프론트엔드와 API 연동**
   - JS fetch로 비동기 API 호출, 단어/인덱스/암기법 등 실시간 표시

---

## 프로젝트 구조 예시

```
bonobono/
├── data_structures/src/         # C 자료구조 소스
│   ├── circular_list.c/h
│   ├── stack.c/h
│   └── queue.c/h
├── vocabulary/
│   ├── views.py                 # Django 뷰(API)
│   ├── c_library.py             # ctypes 연동
│   └── models.py
├── templates/vocabulary/        # HTML 템플릿
├── static/                      # JS, CSS
├── manage.py
└── requirements.txt
```

---

## 정리

- **BONOBONO**는 C로 구현한 자료구조(큐, 스택, 원형 연결 리스트)를 Python/Django 서비스에 실전 활용한 영어 단어 학습 시스템입니다.
- 각 자료구조는 퀴즈 출제, 오답 복습 등 실제 서비스 기능과 밀접하게 연동되어 있습니다.
- 오답 복습의 인덱스 계산 등 세밀한 부분까지 C와 Python의 연동을 최적화하였습니다.

--- 