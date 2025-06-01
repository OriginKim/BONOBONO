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
    Node* newNode = (Node*)malloc(sizeof(Node));
    strcpy(newNode->data.word, word.word);
    strcpy(newNode->data.meaning, word.meaning);
    
    if (list->head == NULL) {
        list->head = newNode;
        newNode->next = newNode;
        list->current = newNode;
    } else {
        newNode->next = list->head->next;
        list->head->next = newNode;
    }
    
    list->size++;
}

Word getCurrentWord(CircularList* list) {
    Word emptyWord = {"", ""};
    if (list->current == NULL) {
        return emptyWord;
    }
    return list->current->data;
}

void moveToNext(CircularList* list) {
    if (list->current != NULL) {
        list->current = list->current->next;
    }
}

void moveToPrevious(CircularList* list) {
    if (list->current != NULL) {
        Node* temp = list->head;
        while (temp->next != list->current) {
            temp = temp->next;
        }
        list->current = temp;
    }
}

int getListSize(CircularList* list) {
    return list->size;
}

void clearList(CircularList* list) {
    if (list->head == NULL) {
        return;
    }
    
    Node* current = list->head->next;
    while (current != list->head) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }
    
    free(list->head);
    list->head = NULL;
    list->current = NULL;
    list->size = 0;
} 