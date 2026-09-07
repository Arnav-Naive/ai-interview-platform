from django.db import models
from django.contrib.auth.models import User
import json


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    resume_file = models.FileField(upload_to='resumes/')
    resume_text = models.TextField(blank=True, default='')
    resume_score = models.IntegerField(default=0)
    suggestions = models.TextField(blank=True, default='[]')  # JSON list
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_suggestions(self):
        try:
            return json.loads(self.suggestions)
        except:
            return []

    def set_suggestions(self, suggestions_list):
        self.suggestions = json.dumps(suggestions_list)

    def __str__(self):
        return f"{self.user.username} - Resume ({self.resume_score}/100)"


class Interview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interviews')
    job_role = models.CharField(max_length=100)
    questions = models.TextField(default='[]')  # JSON list of questions
    answers = models.TextField(default='[]')    # JSON list of answers
    scores = models.TextField(default='[]')     # JSON list of per-question scores
    feedback = models.TextField(default='[]')   # JSON list of per-question feedback
    total_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_questions(self):
        try:
            return json.loads(self.questions)
        except:
            return []

    def get_answers(self):
        try:
            return json.loads(self.answers)
        except:
            return []

    def get_scores(self):
        try:
            return json.loads(self.scores)
        except:
            return []

    def get_feedback(self):
        try:
            return json.loads(self.feedback)
        except:
            return []

    def __str__(self):
        return f"{self.user.username} - {self.job_role} ({self.total_score}/50)"


class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results')
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True)
    interview = models.ForeignKey(Interview, on_delete=models.SET_NULL, null=True, blank=True)
    resume_score = models.IntegerField(default=0)
    interview_score = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    strengths = models.TextField(default='[]')   # JSON
    weaknesses = models.TextField(default='[]')  # JSON
    suggestions = models.TextField(default='[]') # JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def get_strengths(self):
        try:
            return json.loads(self.strengths)
        except:
            return []

    def get_weaknesses(self):
        try:
            return json.loads(self.weaknesses)
        except:
            return []

    def get_suggestions(self):
        try:
            return json.loads(self.suggestions)
        except:
            return []

    def __str__(self):
        return f"{self.user.username} - Total: {self.total_score}/150 ({self.created_at.strftime('%Y-%m-%d')})"
