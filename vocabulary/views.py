from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Word, Quiz, QuizWord, StudentAnswer, WrongWord, LearningStats, WordStats, StudentLog
from .c_library import WordLearningLibrary, Word as CWord
from datetime import datetime, timedelta
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from ctypes import byref
from django.contrib import messages
from django.utils import timezone

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:  # 선생님
            quizzes = Quiz.objects.filter(created_by=request.user)
            return render(request, 'vocabulary/teacher_index.html', {'quizzes': quizzes})
        else:  # 학생
            available_quizzes = Quiz.objects.all()
            
            # 오늘의 통계
            today = datetime.now().date()
            today_stats = LearningStats.objects.filter(
                student=request.user,
                date=today
            ).first()
            
            if not today_stats:
                today_stats = {
                    'total_words': 0,
                    'accuracy_rate': 0,
                    'study_time': 0
                }
            
            # 각 퀴즈의 단어 수 계산
            for quiz in available_quizzes:
                quiz.word_count = QuizWord.objects.filter(quiz=quiz).count()
            
            return render(request, 'vocabulary/student_index.html', {
                'quizzes': available_quizzes,
                'today_stats': today_stats
            })
    return render(request, 'vocabulary/index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('vocabulary:index')
    return render(request, 'vocabulary/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        
        if password1 != password2:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, 'vocabulary/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '이미 사용 중인 아이디입니다.')
            return render(request, 'vocabulary/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '이미 사용 중인 이메일입니다.')
            return render(request, 'vocabulary/register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        login(request, user)
        messages.success(request, '회원가입이 완료되었습니다.')
        return redirect('vocabulary:index')
    return render(request, 'vocabulary/register.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('vocabulary:index')

@login_required
def create_quiz(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        word_ids = request.POST.getlist('words')
        time_limit = int(request.POST.get('time_limit', 60))
        active_from = request.POST.get('active_from')
        active_until = request.POST.get('active_until')
        
        if not word_ids:
            messages.error(request, '최소 하나 이상의 단어를 선택해주세요.')
            return redirect('vocabulary:create_quiz')
        
        # 시작/종료 시간이 유효한지 확인
        active_from_dt = datetime.strptime(active_from, '%Y-%m-%dT%H:%M')
        active_until_dt = datetime.strptime(active_until, '%Y-%m-%dT%H:%M')
        
        # naive datetime을 aware datetime으로 변환
        active_from_dt = timezone.make_aware(active_from_dt)
        active_until_dt = timezone.make_aware(active_until_dt)
        now = timezone.now()
        
        if active_from_dt >= active_until_dt:
            messages.error(request, '시작 시간은 종료 시간보다 빨라야 합니다.')
            return redirect('vocabulary:create_quiz')
        if active_until_dt <= now:
            messages.error(request, '종료 시간은 현재 시간보다 이후여야 합니다.')
            return redirect('vocabulary:create_quiz')
        if time_limit < 30 or time_limit > 3600:
            messages.error(request, '시간 제한은 30초에서 3600초(1시간) 사이여야 합니다.')
            return redirect('vocabulary:create_quiz')
        
        quiz = Quiz.objects.create(
            title=title,
            description=description,
            created_by=request.user,
            time_limit=time_limit,
            active_from=active_from_dt,
            active_until=active_until_dt
        )
        
        # 선택된 단어들을 직접 QuizWord로 생성
        for order, word_id in enumerate(word_ids, 1):
            word = Word.objects.get(id=word_id)
            QuizWord.objects.create(
                quiz=quiz,
                word=word,
                order=order
            )
        
        messages.success(request, '퀴즈가 성공적으로 생성되었습니다.')
        return redirect('vocabulary:quiz_detail', quiz_id=quiz.id)
    
    words = Word.objects.all().order_by('english')
    return render(request, 'vocabulary/create_quiz.html', {'words': words})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # 선생님이 아니거나, 선생님이지만 자신이 만든 퀴즈가 아닌 경우
    if not request.user.is_staff or (request.user.is_staff and quiz.created_by != request.user):
        messages.error(request, '접근 권한이 없습니다.')
        return redirect('vocabulary:index')
    
    # 퀴즈의 단어들을 순서대로 가져옵니다
    quiz_words = QuizWord.objects.filter(quiz=quiz).select_related('word').order_by('order')
    
    # 각 QuizWord 객체의 word 속성이 제대로 로드되었는지 확인
    for qw in quiz_words:
        if not hasattr(qw, 'word') or not qw.word:
            qw.word = Word.objects.get(id=qw.word_id)
    
    context = {
        'quiz': quiz,
        'quiz_words': quiz_words,
        'word_count': quiz_words.count()
    }
    
    return render(request, 'vocabulary/quiz_detail.html', context)

@login_required
def take_quiz(request, quiz_id):
    if request.user.is_staff:
        return redirect('vocabulary:index')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        # Stack을 사용하여 오답 저장
        library = WordLearningLibrary()
        stack = library.create_stack()
        
        quiz_words = QuizWord.objects.filter(quiz=quiz).select_related('word')
        for quiz_word in quiz_words:
            answer = request.POST.get(f'answer_{quiz_word.word.id}')
            is_correct = answer.lower() == quiz_word.word.korean.lower()
            
            StudentAnswer.objects.create(
                student=request.user,
                quiz=quiz,
                word=quiz_word.word,
                answer=answer,
                is_correct=is_correct
            )
            
            if not is_correct:
                WrongWord.objects.get_or_create(student=request.user, word=quiz_word.word)
        
        return redirect('vocabulary:wrong_words')
    
    # 퀴즈의 단어들을 순서대로 가져옵니다
    quiz_words = QuizWord.objects.filter(quiz=quiz).select_related('word').order_by('order')
    
    context = {
        'quiz': quiz,
        'words': quiz_words  # QuizWord 객체 전체를 전달
    }
    return render(request, 'vocabulary/take_quiz.html', context)

@login_required
def wrong_words(request):
    if request.user.is_staff:
        return redirect('vocabulary:index')
    
    wrong_words = WrongWord.objects.filter(student=request.user)
    return render(request, 'vocabulary/wrong_words.html', {'wrong_words': wrong_words})

@login_required
def review_wrong_words(request):
    if request.user.is_staff:
        return redirect('vocabulary:index')
    
    # 원형 연결 리스트를 사용하여 오답 단어 복습
    library = WordLearningLibrary()
    circular_list = library.create_circular_list()
    
    wrong_words = WrongWord.objects.filter(student=request.user)
    for wrong_word in wrong_words:
        word = wrong_word.word
        library.lib.insertWord(circular_list, word.word.encode(), word.meaning.encode())
    
    return render(request, 'vocabulary/review_wrong_words.html', {'wrong_words': wrong_words})

def stats_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # 오늘의 통계
    today = datetime.now().date()
    today_stats = LearningStats.objects.filter(
        student=request.user,
        date=today
    ).first()
    
    if not today_stats:
        today_stats = {
            'total_words': 0,
            'accuracy_rate': 0,
            'study_time': 0
        }
    
    # 최근 7일간의 학습 추이
    last_week = today - timedelta(days=7)
    daily_stats = LearningStats.objects.filter(
        student=request.user,
        date__gte=last_week
    ).order_by('date')
    
    dates = []
    word_counts = []
    accuracy_rates = []
    
    for stat in daily_stats:
        dates.append(stat.date.strftime('%m/%d'))
        word_counts.append(stat.total_words)
        accuracy_rates.append(stat.accuracy_rate)
    
    # 어려운 단어 TOP 10
    difficult_words = WordStats.objects.filter(
        student=request.user
    ).order_by('wrong_count')[:10]
    
    context = {
        'today_stats': today_stats,
        'dates': dates,
        'word_counts': word_counts,
        'accuracy_rates': accuracy_rates,
        'difficult_words': difficult_words
    }
    
    return render(request, 'vocabulary/stats.html', context)

@login_required
def student_logs(request):
    if not request.user.is_staff:
        messages.error(request, '접근 권한이 없습니다.')
        return redirect('vocabulary:index')
    
    # 퀴즈별 학생 성적 통계
    quiz_stats = Quiz.objects.filter(created_by=request.user).annotate(
        total_students=Count('studentanswer__student', distinct=True),
        avg_score=Avg('studentanswer__is_correct')
    ).order_by('-created_at')
    
    # 최근 학생 활동 로그
    recent_logs = StudentAnswer.objects.filter(
        quiz__created_by=request.user
    ).select_related('student', 'quiz', 'word').order_by('-created_at')[:10]
    
    context = {
        'quiz_stats': quiz_stats,
        'recent_logs': recent_logs,
    }
    return render(request, 'vocabulary/student_logs.html', context)
