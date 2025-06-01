#ifndef STACK_H
#define STACK_H

#define MAX_STACK_SIZE 100

typedef struct {
    char word[100];
    char meaning[255];
} Word;

typedef struct {
    Word items[MAX_STACK_SIZE];
    int top;
} Stack;

// Stack 초기화
void initStack(Stack *s);

// Stack이 비어있는지 확인
int isStackEmpty(Stack *s);

// Stack이 가득 찼는지 확인
int isStackFull(Stack *s);

// Stack에 단어 추가
int push(Stack *s, Word word);

// Stack에서 단어 제거
Word pop(Stack *s);

// Stack의 최상단 단어 확인
Word peek(Stack *s);

// Stack의 현재 크기 반환
int getStackSize(Stack *s);

#endif 