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
        self.lib.initQueue.argtypes = [c_void_p]
        self.lib.isQueueEmpty.argtypes = [c_void_p]
        self.lib.isQueueEmpty.restype = c_int
        self.lib.isQueueFull.argtypes = [c_void_p]
        self.lib.isQueueFull.restype = c_int
        self.lib.enqueue.argtypes = [c_void_p, Word]  # Word 구조체를 값으로 전달
        self.lib.enqueue.restype = c_int
        self.lib.dequeue.argtypes = [c_void_p]
        self.lib.dequeue.restype = Word  # Word 구조체를 값으로 반환
        self.lib.getQueueSize.argtypes = [c_void_p]
        self.lib.getQueueSize.restype = c_int
        
        # Stack 함수 설정
        self.lib.initStack.argtypes = [c_void_p]
        self.lib.isStackEmpty.argtypes = [c_void_p]
        self.lib.isStackEmpty.restype = c_int
        self.lib.isStackFull.argtypes = [c_void_p]
        self.lib.isStackFull.restype = c_int
        self.lib.push.argtypes = [c_void_p, c_char_p, c_char_p]
        self.lib.push.restype = c_int
        self.lib.pop.argtypes = [c_void_p]
        self.lib.pop.restype = c_void_p
        self.lib.peek.argtypes = [c_void_p]
        self.lib.peek.restype = c_void_p
        self.lib.getStackSize.argtypes = [c_void_p]
        self.lib.getStackSize.restype = c_int
        
        # Circular List 함수 설정
        self.lib.initCircularList.argtypes = [c_void_p]
        self.lib.insertWord.argtypes = [c_void_p, c_char_p, c_char_p]
        self.lib.getCurrentWord.argtypes = [c_void_p]
        self.lib.getCurrentWord.restype = c_void_p
        self.lib.moveToNext.argtypes = [c_void_p]
        self.lib.moveToPrevious.argtypes = [c_void_p]
        self.lib.getListSize.argtypes = [c_void_p]
        self.lib.getListSize.restype = c_int
        self.lib.clearList.argtypes = [c_void_p]
        self.lib.createQueue.restype = c_void_p
    
    def create_queue(self):
        return self.lib.createQueue()
    
    def create_stack(self):
        stack = c_void_p()
        self.lib.initStack(byref(stack))
        return stack
    
    def create_circular_list(self):
        circular_list = c_void_p()
        self.lib.initCircularList(byref(circular_list))
        return circular_list 