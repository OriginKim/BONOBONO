#include "circular_list.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

void initCircularList(CircularList* list) {
    list->head = NULL;
    list->current = NULL;
    list->size = 0;
}

void insertWord(CircularList* list, Word word) {
    printf("[DEBUG] insertWord 진입: list=%p, word=%s, meaning=%s\n", list, word.word, word.meaning);
    printf("[DEBUG] 현재 상태: head=%p, current=%p, size=%d\n", list->head, list->current, list->size);
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (!newNode) {
        printf("[DEBUG] ❌ Memory allocation failed in insertWord\n");
        return;
    }
    printf("[DEBUG] newNode 할당: %p\n", newNode);

    // word, meaning 값이 NULL일 수 있으므로 방어 코드
    // 무조건 strncpy 사용, NULL 비교 제거
    strncpy(newNode->data.word, word.word, sizeof(newNode->data.word) - 1); 
    newNode->data.word[sizeof(newNode->data.word) - 1] = '\0';

    strncpy(newNode->data.meaning, word.meaning, sizeof(newNode->data.meaning) - 1);
    newNode->data.meaning[sizeof(newNode->data.meaning) - 1] = '\0';

    if (list->head == NULL) {
        newNode->next = newNode;
        list->head = newNode;
        list->current = newNode;
        printf("[DEBUG] Inserted first node: %s\n", newNode->data.word);
    } else {
        Node* tail = list->head;
        int count = 0;
        printf("[DEBUG] tail 탐색 시작: head=%p\n", list->head);
        while (tail->next != list->head && count < list->size + 1) {
            printf("[DEBUG] tail=%p, tail->next=%p\n", tail, tail->next);
            tail = tail->next;
            count++;
        }
        if (count >= list->size + 1) {
            printf("[DEBUG] insertWord: tail 탐색 중 무한루프 감지! 리스트 구조 깨짐\n");
            free(newNode);
            return;
        }
        printf("[DEBUG] tail 찾음: tail=%p, tail->next=%p, head=%p\n", tail, tail->next, list->head);
        tail->next = newNode;
        newNode->next = list->head;
        printf("[DEBUG] Inserted another node: %s, newNode->next=%p, head=%p\n", newNode->data.word, newNode->next, list->head);
    }
    list->size++;
    printf("[DEBUG] insertWord 탈출: list->size=%d, head=%p, current=%p\n", list->size, list->head, list->current);
}

Word getCurrentWord(CircularList* list) {
    printf("[DEBUG] getCurrentWord 진입: list=%p\n", list);
    Word emptyWord = {"", ""};
    if (list->current == NULL) {
        printf("[DEBUG] getCurrentWord: current is NULL\n");
        return emptyWord;
    }
    printf("[DEBUG] getCurrentWord: current word=%s\n", list->current->data.word);
    return list->current->data;
}

void moveToNext(CircularList* list) {
    printf("[DEBUG] moveToNext 진입: list=%p, current=%p, head=%p, size=%d\n", list, list->current, list->head, list->size);
    if (list->current != NULL) {
        if (list->current->next == NULL) {
            printf("[DEBUG] moveToNext: current->next is NULL! (포인터 깨짐)\n");
            return;
        }
        printf("[DEBUG] moveToNext: current=%p, current->next=%p\n", list->current, list->current->next);
        list->current = list->current->next;
        printf("[DEBUG] moveToNext 후: current=%p, current->word=%s\n", list->current, list->current->data.word);
    } else {
        printf("[DEBUG] moveToNext: current is NULL\n");
    }
}

void moveToPrevious(CircularList* list) {
    printf("[DEBUG] moveToPrevious 진입: list=%p, current=%p, head=%p, size=%d\n", list, list->current, list->head, list->size);
    if (list->current != NULL) {
        Node* temp = list->head;
        printf("[DEBUG] moveToPrevious: head=%p\n", list->head);
        int count = 0;
        while (temp->next != list->current && count < list->size + 1) {
            printf("[DEBUG] moveToPrevious: temp=%p, temp->next=%p\n", temp, temp->next);
            temp = temp->next;
            count++;
        }
        if (count >= list->size + 1) {
            printf("[DEBUG] moveToPrevious: 무한루프 감지! 리스트 구조 깨짐\n");
            return;
        }
        list->current = temp;
        printf("[DEBUG] moveToPrevious: new current=%p, word=%s\n", list->current, list->current->data.word);
    } else {
        printf("[DEBUG] moveToPrevious: current is NULL\n");
    }
}

int getListSize(CircularList* list) {
    printf("[DEBUG] getListSize: list=%p, size=%d\n", list, list->size);
    return list->size;
}

void clearList(CircularList* list) {
    printf("[DEBUG] clearList 진입: list=%p\n", list);
    if (list->head == NULL) {
        printf("[DEBUG] clearList: head is NULL\n");
        return;
    }
    Node* current = list->head->next;
    while (current != list->head) {
        Node* temp = current;
        printf("[DEBUG] clearList: free node %p\n", temp);
        current = current->next;
        free(temp);
    }
    printf("[DEBUG] clearList: free head %p\n", list->head);
    free(list->head);
    list->head = NULL;
    list->current = NULL;
    list->size = 0;
    printf("[DEBUG] clearList 탈출\n");
}

CircularList* createCircularList(void) {
    printf("[DEBUG] createCircularList 진입\n");
    CircularList* list = (CircularList*)malloc(sizeof(CircularList));
    if (!list) {
        printf("[DEBUG] ❌ Memory allocation failed in createCircularList\n");
        return NULL;
    }
    printf("[DEBUG] createCircularList: 할당된 list=%p\n", list);
    initCircularList(list);
    printf("[DEBUG] createCircularList 탈출: list=%p\n", list);
    return list;
} 

void moveToHead(CircularList* list) {
    if (list && list->head) {
        list->current = list->head;
    }
}