#ifndef CIRCULAR_LIST_H
#define CIRCULAR_LIST_H

typedef struct {
    char word[100];
    char meaning[255];
} Word;

typedef struct Node {
    Word data;
    struct Node* next;
} Node;

typedef struct {
    Node* head;
    Node* current;
    int size;
} CircularList;

// 원형 연결 리스트 초기화
void initCircularList(CircularList* list);

// 원형 연결 리스트에 단어 추가
void insertWord(CircularList* list, Word word);

// 현재 단어 가져오기
Word getCurrentWord(CircularList* list);

// 다음 단어로 이동
void moveToNext(CircularList* list);

// 이전 단어로 이동
void moveToPrevious(CircularList* list);

// 리스트의 크기 반환
int getListSize(CircularList* list);

// 리스트 비우기
void clearList(CircularList* list);

// 헤드로 이동
void moveToHead(CircularList* list);

#endif 