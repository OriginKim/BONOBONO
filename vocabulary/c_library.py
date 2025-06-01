import ctypes
from ctypes import *
import os
from django.conf import settings

# Word 구조체 정의
class Word(Structure):
    _fields_ = [
        ("word", c_char * 100),
        ("meaning", c_char * 255)
    ]

class WordLearningLibrary:
    def __init__(self):
        self.lib = ctypes.CDLL(settings.C_LIBRARY_PATH)
        
        # Queue 함수 설정
        self.lib.createQueue.restype = c_void_p
        self.lib.initQueue.argtypes = [c_void_p]
        self.lib.isQueueEmpty.argtypes = [c_void_p]
        self.lib.isQueueEmpty.restype = c_int
        self.lib.isQueueFull.argtypes = [c_void_p]
        self.lib.isQueueFull.restype = c_int
        self.lib.enqueue.argtypes = [c_void_p, Word]
        self.lib.enqueue.restype = c_int
        self.lib.dequeue.argtypes = [c_void_p]
        self.lib.dequeue.restype = Word
        self.lib.getQueueSize.argtypes = [c_void_p]
        self.lib.getQueueSize.restype = c_int
        
        # Stack 함수 설정
        self.lib.initStack.restype = c_void_p
        self.lib.isStackEmpty.argtypes = [c_void_p]
        self.lib.isStackEmpty.restype = c_int
        self.lib.isStackFull.argtypes = [c_void_p]
        self.lib.isStackFull.restype = c_int
        self.lib.push.argtypes = [c_void_p, c_char_p, c_char_p]
        self.lib.push.restype = c_int
        self.lib.pop.argtypes = [c_void_p]
        self.lib.pop.restype = Word
        self.lib.peek.argtypes = [c_void_p]
        self.lib.peek.restype = Word
        self.lib.getStackSize.argtypes = [c_void_p]
        self.lib.getStackSize.restype = c_int
        
        # Circular List 함수 설정
        self.lib.initCircularList.argtypes = [c_void_p]
        self.lib.insertWord.argtypes = [c_void_p, c_char_p, c_char_p]
        self.lib.getCurrentWord.argtypes = [c_void_p]
        self.lib.getCurrentWord.restype = POINTER(Word)
        self.lib.moveToNext.argtypes = [c_void_p]
        self.lib.moveToPrevious.argtypes = [c_void_p]
        self.lib.getListSize.argtypes = [c_void_p]
        self.lib.getListSize.restype = c_int
        self.lib.clearList.argtypes = [c_void_p]
    
    def create_queue(self):
        return self.lib.createQueue()
    
    def create_stack(self):
        return self.lib.initStack()
    
    def create_circular_list(self):
        circular_list = c_void_p()
        self.lib.initCircularList(byref(circular_list))
        return circular_list
    
    def push_word(self, stack, english, korean):
        return self.lib.push(stack, english.encode('utf-8'), korean.encode('utf-8'))
    
    def pop_word(self, stack):
        try:
            word = self.lib.pop(stack)
            if word.word:
                return {
                    'english': word.word.decode('utf-8'),
                    'korean': word.meaning.decode('utf-8')
                }
        except Exception as e:
            print(f"pop_word 오류: {str(e)}")
        return None 