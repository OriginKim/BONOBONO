from django.urls import path
from . import views

app_name = 'vocabulary'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # 선생님 전용 URL
    path('teacher/quiz/create/', views.create_quiz, name='create_quiz'),
    path('teacher/quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('teacher/student-logs/', views.student_logs, name='student_logs'),
    path('teacher/quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    
    # 학생 전용 URL
    path('student/quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('student/wrong-words/', views.wrong_words, name='wrong_words'),
    path('student/wrong-words/review/', views.review_wrong_words, name='review_wrong_words'),
    path('student/difficult-words/', views.difficult_words, name='difficult_words'),
    path('student/stats/', views.stats_view, name='stats'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/student-results/', views.quiz_student_results, name='quiz_student_results'),
    path('api/association/', views.generate_association, name='generate_association'),
    path('api/next_wrong_word/', views.api_next_wrong_word, name='api_next_wrong_word'),
    path('api/prev_wrong_word/', views.api_prev_wrong_word, name='api_prev_wrong_word'),
    path('api/debug-enqueue-word/', views.debug_enqueue_word, name='debug_enqueue_word'),
] 