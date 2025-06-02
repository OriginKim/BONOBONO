from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Word, Quiz, QuizWord, StudentAnswer, WrongWord, LearningStats, WordStats, StudentLog
from .c_library import WordLearningLibrary, Word as CWord
from datetime import datetime, timedelta
from django.db.models import Count, Avg, FloatField
from django.db.models.functions import TruncDate
from ctypes import byref
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import logging
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import traceback
import openai
import os
from dotenv import load_dotenv
from django.urls import reverse
import ctypes

# 로거 설정
logger = logging.getLogger(__name__)

# .env 파일을 자동으로 불러오도록 추가
load_dotenv()

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:  # 선생님
            quizzes = Quiz.objects.filter(created_by=request.user)
            return render(request, 'vocabulary/teacher_index.html', {'quizzes': quizzes})
        else:  # 학생
            now = timezone.now()
            available_quizzes = Quiz.objects.filter(
                active_from__lte=now,  # 시작 시간이 현재보다 이전
                active_until__gt=now   # 종료 시간이 현재보다 이후
            )
            
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
            
            # 아직 시작하지 않은 퀴즈
            upcoming_quizzes = Quiz.objects.filter(
                active_from__gt=now
            ).order_by('active_from')
            
            # 이미 종료된 퀴즈
            expired_quizzes = Quiz.objects.filter(
                active_until__lte=now
            ).order_by('-active_until')
            
            return render(request, 'vocabulary/student_index.html', {
                'quizzes': available_quizzes,
                'upcoming_quizzes': upcoming_quizzes,
                'expired_quizzes': expired_quizzes,
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
        
        # C 큐 생성 및 단어 enqueue
        library = WordLearningLibrary()
        queue = library.create_queue()
        for order, word_id in enumerate(word_ids, 1):
            word = Word.objects.get(id=word_id)
            QuizWord.objects.create(
                quiz=quiz,
                word=word,
                order=order
            )
            # C 큐에 단어 enqueue
            try:
                library.enqueue_word(queue, word.id)
            except Exception as e:
                logger.error(f"C 큐 enqueue 실패: {str(e)}")
        # (여기서는 큐를 세션/DB에 저장하지 않음, 실제 사용은 take_quiz에서)
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
    now = timezone.now()
    
    # 퀴즈 시간 체크
    if now < quiz.active_from:
        messages.warning(request, f'이 퀴즈는 {quiz.active_from.strftime("%Y년 %m월 %d일 %H시 %M분")}부터 풀 수 있습니다.')
        return redirect('vocabulary:index')
    elif now > quiz.active_until:
        messages.warning(request, f'이 퀴즈는 {quiz.active_until.strftime("%Y년 %m월 %d일 %H시 %M분")}에 종료되었습니다.')
        return redirect('vocabulary:index')
    
    if request.method == 'POST':
        try:
            library = WordLearningLibrary()
            stack = None
            try:
                stack = library.create_stack()
            except Exception as e:
                logger.error(f"Stack creation failed: {str(e)}")
            # C 큐 생성 및 퀴즈 단어 enqueue
            queue = library.create_queue()
            quiz_words = QuizWord.objects.filter(quiz=quiz).select_related('word').order_by('order')
            for quiz_word in quiz_words:
                try:
                    library.enqueue_word(queue, quiz_word.word.id)
                except Exception as e:
                    logger.error(f"C 큐 enqueue 실패(응시): {str(e)}")
            answers = []
            correct_count = 0
            total_count = 0
            # C 큐에서 dequeue로 단어를 꺼내 문제 출제
            for _ in range(len(quiz_words)):
                word_info = library.dequeue_word(queue)
                if not word_info:
                    continue
                word_id = None
                # DB에서 word_id 찾기
                for qw in quiz_words:
                    if qw.word.english == word_info['english'] and qw.word.korean == word_info['korean']:
                        word_id = qw.word.id
                        break
                if word_id is None:
                    continue
                answer = request.POST.get(f'answer_{word_id}', '').strip()
                is_correct = answer.lower() == word_info['korean'].lower()
                StudentAnswer.objects.create(
                    student=request.user,
                    quiz=quiz,
                    word_id=word_id,
                    answer=answer,
                    is_correct=is_correct
                )
                if not is_correct:
                    wrong_word_obj, created = WrongWord.objects.get_or_create(student=request.user, word_id=word_id)
                    if not created:
                        wrong_word_obj.wrong_count += 1
                        wrong_word_obj.save()
                    if stack:
                        try:
                            library.push_word(stack, word_id)
                        except Exception as e:
                            logger.error(f"Stack push failed: {str(e)}")
                answers.append({
                    'word': word_info,
                    'user_answer': answer,
                    'is_correct': is_correct
                })
                total_count += 1
                if is_correct:
                    correct_count += 1
            score = (correct_count / total_count) * 100 if total_count > 0 else 0
            return render(request, 'vocabulary/quiz_result.html', {
                'quiz': quiz,
                'answers': answers,
                'score': round(score, 1),
                'correct_count': correct_count,
                'total_count': total_count
            })
        except Exception as e:
            logger.error(f"Quiz submission error: {str(e)}")
            messages.error(request, '퀴즈 제출 중 오류가 발생했습니다. 다시 시도해주세요.')
            return redirect('vocabulary:take_quiz', quiz_id=quiz_id)
    
    # 퀴즈의 단어들을 순서대로 가져옵니다
    quiz_words = QuizWord.objects.filter(quiz=quiz).select_related('word').order_by('order')
    
    context = {
        'quiz': quiz,
        'words': quiz_words
    }
    return render(request, 'vocabulary/take_quiz.html', context)

@login_required
def wrong_words(request):
    if request.user.is_staff:
        return redirect('vocabulary:index')
    # 가장 최근에 틀린 단어가 맨 위에 오도록 정렬
    wrong_words = WrongWord.objects.filter(student=request.user).order_by('-last_wrong_date')
    return render(request, 'vocabulary/wrong_words.html', {'wrong_words': wrong_words})

def get_current_index(library, circular_list):
    total_count = library.get_circular_list_size(circular_list)
    if total_count == 0:
        return 0, 0
    # head로 이동
    library.lib.moveToHead(circular_list)
    index = 1
    for _ in range(total_count):
        word_struct = library.lib.getCurrentWord(circular_list)
        # current가 가리키는 노드와 같으면 break
        if word_struct.word == library.lib.getCurrentWord(circular_list).word and \
           word_struct.meaning == library.lib.getCurrentWord(circular_list).meaning:
            break
        library.lib.moveToNext(circular_list)
        index += 1
    return index, total_count

@login_required
def review_wrong_words(request):
    if request.user.is_staff:
        return redirect('vocabulary:index')
    try:
        library = WordLearningLibrary()
        stack = library.create_stack()
        wrong_words = WrongWord.objects.filter(student=request.user).order_by('-last_wrong_date')
        # 스택에 단어 추가
        for wrong_word in wrong_words:
            library.push_word(stack, wrong_word.word.id)
        # 원형 리스트 생성 및 단어 추가
        circular_list = library.create_circular_list()
        if not circular_list:
            messages.error(request, '오답 복습을 시작할 수 없습니다.')
            return redirect('vocabulary:wrong_words')
        for _ in range(len(wrong_words)):
            word_info = library.pop_word(stack)
            if word_info:
                library.insert_word_to_list(circular_list, word_info['english'], word_info['korean'])
        # 세션에 circular_list 포인터 저장
        request.session['circular_list_ptr'] = str(int(circular_list))
        # 현재 단어 가져오기
        current_word_struct = library.lib.getCurrentWord(circular_list)
        if not current_word_struct.word:
            messages.error(request, '원형 리스트에 단어가 없습니다.')
            return redirect('vocabulary:wrong_words')
        try:
            current_word = {
                "english": current_word_struct.word.decode("utf-8"),
                "korean": current_word_struct.meaning.decode("utf-8")
            }
        except Exception as e:
            logger.error(f"getCurrentWord 포인터 접근 에러: {e}")
            messages.error(request, '단어 정보를 불러오는 데 실패했습니다.')
            return redirect('vocabulary:wrong_words')
        # 인덱스 계산 (C 함수 직접 호출)
        index = library.lib.getCurrentIndex(circular_list)
        total_count = library.get_circular_list_size(circular_list)
        return render(request, 'vocabulary/review_wrong_words.html', {
            'current_word': current_word,
            'has_words': len(wrong_words) > 0,
            'current_index': index,
            'total_count': total_count
        })
    except Exception as e:
        logger.error(f"Error in review_wrong_words: {str(e)}")
        messages.error(request, '오답 복습 중 오류가 발생했습니다.')
        return redirect('vocabulary:wrong_words')

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
        avg_score=Avg('studentanswer__is_correct', output_field=FloatField()) * 100  # 백분율로 변환
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

@login_required
def quiz_student_results(request, quiz_id):
    if not request.user.is_staff:
        return JsonResponse({'error': '접근 권한이 없습니다.'}, status=403)
    
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    # 학생별 답변 데이터 수집
    student_answers = StudentAnswer.objects.filter(
        quiz=quiz
    ).select_related('student', 'word').order_by('student__username', 'created_at')
    
    # 학생별로 데이터 그룹화
    student_data = {}
    for answer in student_answers:
        if answer.student.username not in student_data:
            student_data[answer.student.username] = {
                'username': answer.student.username,
                'answers': [],
                'correct_count': 0,
                'total_count': 0
            }
        
        student_data[answer.student.username]['answers'].append({
            'word': answer.word.english,
            'answer': answer.answer,
            'is_correct': answer.is_correct
        })
        
        student_data[answer.student.username]['total_count'] += 1
        if answer.is_correct:
            student_data[answer.student.username]['correct_count'] += 1
    
    # 점수 계산 및 데이터 정리
    students = []
    for username, data in student_data.items():
        score = (data['correct_count'] / data['total_count']) * 100 if data['total_count'] > 0 else 0
        students.append({
            'username': username,
            'score': round(score, 1),
            'answers': data['answers']
        })
    
    # 점수순으로 정렬
    students.sort(key=lambda x: x['score'], reverse=True)
    
    return JsonResponse({
        'quiz_title': quiz.title,
        'students': students
    })

@login_required
def difficult_words(request):
    if request.user.is_staff:
        return redirect('vocabulary:index')
    try:
        # 학생이 틀린 단어들을 가져와서 틀린 횟수별로 그룹화
        wrong_words = WrongWord.objects.filter(student=request.user)
        difficulty_groups = {}
        for wrong_word in wrong_words:
            count = wrong_word.wrong_count
            if count not in difficulty_groups:
                difficulty_groups[count] = []
            difficulty_groups[count].append(wrong_word)
        # 틀린 횟수가 많은 순서대로 정렬
        sorted_groups = sorted(difficulty_groups.items(), reverse=True)
        context = {
            'sorted_groups': sorted_groups,
            'total_wrong_words': wrong_words.count()
        }
        return render(request, 'vocabulary/difficult_words.html', context)
    except Exception as e:
        traceback.print_exc()
        messages.error(request, f'오류가 발생했습니다: {str(e)}')
        return redirect('vocabulary:index')

@csrf_exempt
@require_POST
def generate_association(request):
    try:
        data = json.loads(request.body)
        word = data.get('word') or data.get('english')
        meaning = data.get('meaning') or data.get('korean')
        if not word or not meaning:
            return JsonResponse({'success': False, 'error': '단어와 뜻을 모두 입력해야 합니다.'}, status=400)

        # OpenAI GPT-3.5 Turbo API 호출 (openai>=1.0.0 방식)
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return JsonResponse({'success': False, 'error': 'OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.'}, status=500)
        client = openai.OpenAI(api_key=api_key)
        prompt = f"단어: {word}\n뜻: {meaning}\n경선식 영어 암기법 예시) eligible: 엘리(eligible)베이터를 탈 자격이 있는 사람만 올라갈 수 있다!\n위와 같이, 이 단어를 쉽게 외울 수 있는 경선식 연상 암기법(재미있는 스토리, 이미지, 연상법 등)을 2~3문장으로 설명해줘."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 경선식 영어 암기법을 잘 만들어주는 선생님이야."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
            top_p=0.8
        )
        association = response.choices[0].message.content.strip()
        return JsonResponse({'success': True, 'association': association})
    except Exception as e:
        import sys
        import traceback
        traceback.print_exc(file=sys.stdout)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, '퀴즈가 삭제되었습니다.')
        return redirect('vocabulary:index')
    return render(request, 'vocabulary/confirm_delete.html', {'quiz': quiz})

@login_required
@require_POST
def api_next_wrong_word(request):
    try:
        library = WordLearningLibrary()
        circular_list_ptr = request.session.get('circular_list_ptr')
        if not circular_list_ptr:
            return JsonResponse({'success': False, 'error': '복습 세션이 만료되었습니다. 페이지를 새로고침 해주세요.'})
        circular_list = ctypes.c_void_p(int(circular_list_ptr))
        library.lib.moveToNext(circular_list)
        word = library.lib.getCurrentWord(circular_list)
        # 인덱스 계산 (C 함수 직접 호출)
        index = library.lib.getCurrentIndex(circular_list)
        total_count = library.get_circular_list_size(circular_list)
        if word.word:
            return JsonResponse({
                'success': True,
                'english': word.word.decode('utf-8'),
                'korean': word.meaning.decode('utf-8'),
                'current_index': index,
                'total_count': total_count
            })
        return JsonResponse({'success': False, 'error': '단어를 불러올 수 없습니다.'})
    except Exception as e:
        logger.error(f"Error in api_next_wrong_word: {str(e)}")
        return JsonResponse({'success': False, 'error': '오류가 발생했습니다.'})

@login_required
@require_POST
def api_prev_wrong_word(request):
    try:
        library = WordLearningLibrary()
        circular_list_ptr = request.session.get('circular_list_ptr')
        if not circular_list_ptr:
            return JsonResponse({'success': False, 'error': '복습 세션이 만료되었습니다. 페이지를 새로고침 해주세요.'})
        circular_list = ctypes.c_void_p(int(circular_list_ptr))
        library.lib.moveToPrevious(circular_list)
        word = library.lib.getCurrentWord(circular_list)
        # 인덱스 계산 (C 함수 직접 호출)
        index = library.lib.getCurrentIndex(circular_list)
        total_count = library.get_circular_list_size(circular_list)
        if word.word:
            return JsonResponse({
                'success': True,
                'english': word.word.decode('utf-8'),
                'korean': word.meaning.decode('utf-8'),
                'current_index': index,
                'total_count': total_count
            })
        return JsonResponse({'success': False, 'error': '단어를 불러올 수 없습니다.'})
    except Exception as e:
        logger.error(f"Error in api_prev_wrong_word: {str(e)}")
        return JsonResponse({'success': False, 'error': '오류가 발생했습니다.'})
