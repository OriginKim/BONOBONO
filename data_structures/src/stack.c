#include "stack.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>  // malloc 포함

Stack* initStack() {
    printf("[DEBUG] initStack: 새로운 스택 초기화\n");
    Stack* s = (Stack*)malloc(sizeof(Stack));
    if (s != NULL) {
        s->top = -1;
        printf("[DEBUG] ✅ initStack 성공: s=%p\n", s);
    } else {
        printf("[DEBUG] ❌ initStack 실패: 메모리 할당 실패\n");
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
    printf("[DEBUG] push 시도: word=%s, meaning=%s\n", word.word, word.meaning);
    if (isStackFull(s)) {
        printf("[DEBUG] ❌ push 실패: 스택이 가득 참\n");
        return 0;  // 실패
    }
    
    s->top++;
    strcpy(s->items[s->top].word, word.word);
    strcpy(s->items[s->top].meaning, word.meaning);
    
    printf("[DEBUG] ✅ push 성공: word=%s, top=%d\n", word.word, s->top);
    return 1;  // 성공
}

Word pop(Stack *s) {
    Word emptyWord = {"", ""};
    
    if (isStackEmpty(s)) {
        printf("[DEBUG] ❌ pop 실패: 스택이 비어있음\n");
        return emptyWord;
    }
    
    Word word = s->items[s->top];
    printf("[DEBUG] pop 시도: word=%s, meaning=%s\n", word.word, word.meaning);
    
    s->top--;
    
    printf("[DEBUG] ✅ pop 성공: word=%s, top=%d\n", word.word, s->top);
    return word;
}

Word peek(Stack *s) {
    Word emptyWord = {"", ""};
    
    if (isStackEmpty(s)) {
        printf("[DEBUG] ❌ peek 실패: 스택이 비어있음\n");
        return emptyWord;
    }
    
    printf("[DEBUG] peek: word=%s, meaning=%s\n", s->items[s->top].word, s->items[s->top].meaning);
    return s->items[s->top];
}

int getStackSize(Stack *s) {
    printf("[DEBUG] getStackSize: size=%d\n", s->top + 1);
    return s->top + 1;
} 