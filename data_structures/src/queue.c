#include "queue.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

void initQueue(Queue *q) {
    printf("[DEBUG] initQueue: 큐 초기화\n");
    q->front = 0;
    q->rear = -1;
    q->size = 0;
}

int isQueueEmpty(Queue *q) {
    return q->size == 0;
}

int isQueueFull(Queue *q) {
    return q->size == MAX_QUEUE_SIZE;
}

int enqueue(Queue *q, Word word) {
    printf("[DEBUG] enqueue 시도: word=%s, meaning=%s\n", word.word, word.meaning);
    if (isQueueFull(q)) {
        printf("[DEBUG] ❌ enqueue 실패: 큐가 가득 참\n");
        return 0;  // 실패
    }
    
    q->rear = (q->rear + 1) % MAX_QUEUE_SIZE;
    strcpy(q->items[q->rear].word, word.word);
    strcpy(q->items[q->rear].meaning, word.meaning);
    q->size++;
    printf("[DEBUG] 큐 상태: front=%d, rear=%d, size=%d\n", q->front, q->rear, q->size);
    printf("[DEBUG] 큐 메모리 주소: %p\n", (void*)q);
    printf("[DEBUG] 단어 배열 메모리 주소: %p\n", (void*)q->items);
    printf("[DEBUG] ✅ enqueue 성공: word=%s, size=%d\n", word.word, q->size);
    return 1;  // 성공
}

Word dequeue(Queue *q) {
    Word emptyWord = {"", ""};
    
    if (isQueueEmpty(q)) {
        printf("[DEBUG] ❌ dequeue 실패: 큐가 비어있음\n");
        return emptyWord;
    }
    
    Word word = q->items[q->front];
    printf("[DEBUG] dequeue 시도: word=%s, meaning=%s\n", word.word, word.meaning);
    
    q->front = (q->front + 1) % MAX_QUEUE_SIZE;
    q->size--;
    
    printf("[DEBUG] ✅ dequeue 성공: word=%s, size=%d\n", word.word, q->size);
    return word;
}

int getQueueSize(Queue *q) {
    printf("[DEBUG] getQueueSize: size=%d\n", q->size);
    return q->size;
}

Queue* createQueue(void) {
    printf("[DEBUG] createQueue: 새로운 큐 생성\n");
    Queue* q = (Queue*)malloc(sizeof(Queue));
    if (q != NULL) {
        initQueue(q);
        printf("[DEBUG] ✅ createQueue 성공: q=%p\n", (void*)q);
    } else {
        printf("[DEBUG] ❌ createQueue 실패: 메모리 할당 실패\n");
    }
    return q;
} 
