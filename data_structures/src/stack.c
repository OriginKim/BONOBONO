#include "stack.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>  // malloc 포함

Stack* initStack() {
    Stack* s = (Stack*)malloc(sizeof(Stack));
    if (s != NULL) {
        s->top = -1;
    }
    return s;
}
int isStackEmpty(Stack *s) {
    return s->top == -1;
}

int isStackFull(Stack *s) {
    return s->top == MAX_STACK_SIZE - 1;
}

int push(Stack *s, Word word) {
    if (isStackFull(s)) {
        return 0;  // 실패
    }
    
    s->top++;
    strcpy(s->items[s->top].word, word.word);
    strcpy(s->items[s->top].meaning, word.meaning);
    
    return 1;  // 성공
}

Word pop(Stack *s) {
    Word emptyWord = {"", ""};
    
    if (isStackEmpty(s)) {
        return emptyWord;
    }
    
    Word word = s->items[s->top];
    s->top--;
    
    return word;
}

Word peek(Stack *s) {
    Word emptyWord = {"", ""};
    
    if (isStackEmpty(s)) {
        return emptyWord;
    }
    
    return s->items[s->top];
}

int getStackSize(Stack *s) {
    return s->top + 1;
} 