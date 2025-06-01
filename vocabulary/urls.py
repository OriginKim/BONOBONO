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
    
    # 학생 전용 URL
    path('student/quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('student/wrong-words/', views.wrong_words, name='wrong_words'),
    path('student/wrong-words/review/', views.review_wrong_words, name='review_wrong_words'),
    path('review-wrong-words/', views.review_wrong_words, name='review_wrong_words'),
    path('stats/', views.stats_view, name='stats'),
] 