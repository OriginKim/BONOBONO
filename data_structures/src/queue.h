#ifndef QUEUE_H
#define QUEUE_H

#define MAX_QUEUE_SIZE 20

typedef struct {
    char word[100];
    char meaning[255];
} Word;

typedef struct {
    Word items[MAX_QUEUE_SIZE];
    int front;
    int rear;
    int size;
} Queue;

// Queue 초기화
void initQueue(Queue *q);

// Queue가 비어있는지 확인
int isQueueEmpty(Queue *q);

// Queue가 가득 찼는지 확인
int isQueueFull(Queue *q);

// Queue에 단어 추가
int enqueue(Queue *q, Word word);

// Queue에서 단어 제거
Word dequeue(Queue *q);

// Queue의 현재 크기 반환
int getQueueSize(Queue *q);

// Queue 생성
Queue* createQueue(void);



#endif 