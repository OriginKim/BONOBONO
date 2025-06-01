from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Word(models.Model):
    english = models.CharField(max_length=100)
    korean = models.CharField(max_length=200)
    part_of_speech = models.CharField(max_length=20)
    difficulty = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    example_sentence = models.TextField(null=True, blank=True)
    example_translation = models.TextField(null=True, blank=True)
    daily_word_date = models.DateField(null=True, blank=True)
    is_bookmarked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.english} - {self.korean}"

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    time_limit = models.IntegerField(default=60, help_text="퀴즈 제한 시간(초)")
    active_from = models.DateTimeField(default=timezone.now, help_text="퀴즈 활성화 시작 시간")
    active_until = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(days=7),
        help_text="퀴즈 활성화 종료 시간"
    )
    words = models.ManyToManyField(Word, through='QuizWord')

    def __str__(self):
        return self.title

    def is_active(self):
        now = timezone.now()
        return self.active_from <= now <= self.active_until

class QuizWord(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - {self.word.english}"

class StudentAnswer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.word.english}"

class WrongWord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    wrong_count = models.IntegerField(default=1)
    last_wrong_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'word')

    def __str__(self):
        return f"{self.student.username} - {self.word.english}"

class LearningStats(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    total_quizzes = models.IntegerField(default=0)
    total_words = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    study_time = models.IntegerField(default=0)  # 분 단위

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.username} - {self.date}"

    @property
    def accuracy_rate(self):
        if self.total_words == 0:
            return 0
        return round((self.correct_answers / self.total_words) * 100, 1)

class WordStats(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    total_attempts = models.IntegerField(default=0)
    correct_attempts = models.IntegerField(default=0)
    last_attempt_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.word.english} - {self.accuracy_rate}%"

    @property
    def accuracy_rate(self):
        if self.total_attempts == 0:
            return 0
        return round((self.correct_attempts / self.total_attempts) * 100, 1)

class StudentLog(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_logs')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='student_logs')
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score}점)"
