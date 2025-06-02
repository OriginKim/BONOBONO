import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# C 라이브러리 경로 설정
C_LIBRARY_PATH = os.path.join(BASE_DIR, 'data_structures', 'src', 'libword_learning.so')

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'vocabulary' / 'static',
]
STATIC_ROOT = os.path.join(str(BASE_DIR), 'staticfiles')

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'vocabulary': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
} 