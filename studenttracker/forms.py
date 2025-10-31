from django import forms
from .models import Course, Task

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['student', 'name', 'status', 'completion_percentage', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'})
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['student', 'course', 'title', 'description', 'deadline', 'status']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4})
        }

