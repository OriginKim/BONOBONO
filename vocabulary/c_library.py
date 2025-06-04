import ctypes
from ctypes import *
import os
from django.conf import settings
import logging
from .models import Word as DjangoWord  # Django DB 모델 불러오기

logger = logging.getLogger(__name__)

# C 구조체 Word 정의 (영어 단어, 뜻)
class Word(Structure):
    _fields_ = [
        ("word", c_char * 100),
        ("meaning", c_char * 255)
    ]

class WordLearningLibrary:
    def __init__(self):
        try:
            # C 라이브러리 로드
            lib_path = settings.C_LIBRARY_PATH
            logger.info(f"Loading C library from: {lib_path}")
            
            if not os.path.exists(lib_path):
                raise FileNotFoundError(f"C library not found at: {lib_path}")
                
            self.lib = ctypes.CDLL(lib_path)
            logger.info("C library loaded successfully")

            # self.lib.getQueueFront.argtypes = [c_void_p]
            # self.lib.getQueueFront.restype = c_int
            # self.lib.getQueueRear.argtypes = [c_void_p]
            # self.lib.getQueueRear.restype = c_int

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
            self.lib.initStack.argtypes = []
            self.lib.isStackEmpty.argtypes = [c_void_p]
            self.lib.isStackEmpty.restype = c_int
            self.lib.isStackFull.argtypes = [c_void_p]
            self.lib.isStackFull.restype = c_int
            self.lib.push.argtypes = [c_void_p, Word]
            self.lib.push.restype = c_int
            self.lib.pop.argtypes = [c_void_p]
            self.lib.pop.restype = Word
            self.lib.peek.argtypes = [c_void_p]
            self.lib.peek.restype = Word
            self.lib.getStackSize.argtypes = [c_void_p]
            self.lib.getStackSize.restype = c_int

            # Circular List 함수 설정
            self.lib.createCircularList.restype = c_void_p
            self.lib.createCircularList.argtypes = []
            self.lib.initCircularList.argtypes = [c_void_p]
            self.lib.insertWord.argtypes = [c_void_p, Word]
            self.lib.getCurrentWord.argtypes = [c_void_p]
            self.lib.getCurrentWord.restype = Word
            self.lib.moveToNext.argtypes = [c_void_p]
            self.lib.moveToPrevious.argtypes = [c_void_p]
            self.lib.getListSize.argtypes = [c_void_p]
            self.lib.getListSize.restype = c_int
            self.lib.clearList.argtypes = [c_void_p]
            self.lib.moveToHead.argtypes = [ctypes.c_void_p]
            self.lib.moveToHead.restype = None
            self.lib.getCurrentIndex.argtypes = [ctypes.c_void_p]
            self.lib.getCurrentIndex.restype = ctypes.c_int

        except Exception as e:
            logger.error(f"Error initializing WordLearningLibrary: {str(e)}")
            raise

    # Queue 관련
    def create_queue(self):
        try:
            queue = self.lib.createQueue()
            if not queue:
                logger.error("Queue creation failed: NULL pointer returned")
                raise RuntimeError("큐 생성 실패: NULL 포인터 반환")
            logger.info("Queue created successfully")
            return queue
        except Exception as e:
            logger.error(f"Error creating queue: {str(e)}")
            raise

    def enqueue_word(self, queue, word_id):
        if not queue:
            logger.error("enqueue_word error: Queue pointer is None")
            return -1
        try:
            db_word = DjangoWord.objects.get(id=word_id)
            c_word = Word()
            c_word.word = db_word.english.encode('utf-8')
            c_word.meaning = db_word.korean.encode('utf-8')
            result = self.lib.enqueue(queue, c_word)
            if result == 0:
                logger.error("Queue is full")
                return -1
            logger.info(f"Word enqueued to queue successfully: {db_word.english}")
            logger.info("\n" + "="*50 + "\n")  # 깔끔한 구분선

            return result
        except DjangoWord.DoesNotExist:
            logger.error(f"enqueue_word error: Word with ID {word_id} not found")
            return -1
        except Exception as e:
            logger.error(f"enqueue_word exception: {str(e)}")
            return -1

    def dequeue_word(self, queue):
        if not queue:
            logger.error("dequeue_word error: Queue pointer is None")
            return None
        try:
            word = self.lib.dequeue(queue)
            if word.word:
                result = {
                    'english': word.word.decode('utf-8').strip(),
                    'korean': word.meaning.decode('utf-8').strip()
                }
                logger.info(f"Word dequeued form queue: {result['english']}")
                logger.info("\n" + "="*50 + "\n")
                return result
                
                
            logger.warning("Empty word returned from dequeue")
            return None
        except Exception as e:
            logger.error(f"dequeue_word error: {str(e)}")
            return None

    # Stack 관련
    def create_stack(self):
        try:
            stack = self.lib.initStack()
            if not stack:
                logger.error("Stack creation failed: NULL pointer returned")
                raise RuntimeError("스택 생성 실패: NULL 포인터 반환")
            logger.info("Stack created successfully")
            return stack
        except Exception as e:
            logger.error(f"Error creating stack: {str(e)}")
            raise

    def push_word(self, stack, word_id):
        if not stack:
            logger.error("push_word error: Stack pointer is None")
            return -1
        try:
            db_word = DjangoWord.objects.get(id=word_id)
            c_word = Word()
            c_word.word = db_word.english.encode('utf-8')
            c_word.meaning = db_word.korean.encode('utf-8')
            result = self.lib.push(stack, c_word)
            if result == 0:
                logger.error("Stack is full")
                return -1
            logger.info(f"Word pushed to stack successfully: {db_word.english}")
            logger.info("\n" + "="*50 + "\n")
            return result
        except DjangoWord.DoesNotExist:
            logger.error(f"push_word error: Word with ID {word_id} not found")
            return -1
        except Exception as e:
            logger.error(f"push_word exception: {str(e)}")
            return -1

    def pop_word(self, stack):
        if not stack:
            logger.error("pop_word error: Stack pointer is None")
            return None
        try:
            word = self.lib.pop(stack)
            if word.word:
                result = {
                    'english': word.word.decode('utf-8').strip(),
                    'korean': word.meaning.decode('utf-8').strip()
                }
                logger.info(f"Word popped from stack: {result['english']}")
                logger.info("\n" + "="*50 + "\n")
                return result
            logger.warning("Empty word returned from pop")
            return None
        except Exception as e:
            logger.error(f"pop_word error: {str(e)}")
            return None
        
    def get_stack_size(self, stack):
        if not stack:
            logger.error("get_stack_size error: Stack pointer is None")
            return 0
        try:
            size = self.lib.getStackSize(stack)
            logger.info(f"Current stack size: {size}")
            return size
        except Exception as e:
            logger.error(f"get_stack_size error: {str(e)}")
            return 0


    def create_circular_list(self):
        try:
            circular_list = self.lib.createCircularList()
            if not circular_list:
                logger.error("Circular list creation failed: NULL pointer returned")
                raise RuntimeError("원형 리스트 생성 실패: NULL 포인터 반환")
            logger.info("Circular list created successfully")
            return circular_list
        except Exception as e:
            logger.error(f"Error creating circular list: {str(e)}")
            raise

    def insert_word_to_list(self, circular_list, english, korean):
        try:
            word = Word()
            word.word = english.encode('utf-8')
            word.meaning = korean.encode('utf-8')
            self.lib.insertWord(circular_list, word)
            logger.info(f"Word inserted to circular list successfully: {english}")
            logger.info("\n" + "="*50 + "\n")
        except Exception as e:
            logger.error(f"Error inserting word to circular list: {str(e)}")
            raise

    def get_circular_list_size(self, circular_list_ptr):
        return self.lib.getListSize(circular_list_ptr)
    
   

