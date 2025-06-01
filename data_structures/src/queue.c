#include "queue.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

void initQueue(Queue *q) {
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
    if (isQueueFull(q)) {
        return 0;  // 실패
    }
    
    q->rear = (q->rear + 1) % MAX_QUEUE_SIZE;
    strcpy(q->items[q->rear].word, word.word);
    strcpy(q->items[q->rear].meaning, word.meaning);
    q->size++;
    
    return 1;  // 성공
}

Word dequeue(Queue *q) {
    Word emptyWord = {"", ""};
    
    if (isQueueEmpty(q)) {
        return emptyWord;
    }
    
    Word word = q->items[q->front];
    q->front = (q->front + 1) % MAX_QUEUE_SIZE;
    q->size--;
    
    return word;
}

int getQueueSize(Queue *q) {
    return q->size;
}

Queue* createQueue(void) {
    Queue* q = (Queue*)malloc(sizeof(Queue));
    initQueue(q);
    return q;
} 