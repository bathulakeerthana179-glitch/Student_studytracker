from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    education = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.username

# NEW: YouTube-style Course Model
class Course(models.Model):
    COURSE_LEVELS = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(default='No description provided')
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    #instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught',null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    level = models.CharField(max_length=20, choices=COURSE_LEVELS, default='beginner')
    duration_hours = models.IntegerField(default=0)
    students_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_video_count(self):
        return Video.objects.filter(section__course=self).count()
    
    class Meta:
        ordering = ['-created_at']

# NEW: Video Section Model (like YouTube playlists)
class VideoSection(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

# NEW: Video Model for YouTube-style content
class Video(models.Model):
    VIDEO_TYPES = (
        ('video', 'Video'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )
    
    section = models.ForeignKey(VideoSection, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_url = models.URLField(help_text="YouTube URL or video file URL", blank=True, null=True)
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    duration = models.IntegerField(help_text="Duration in seconds", default=0)
    order = models.IntegerField(default=0)
    video_type = models.CharField(max_length=20, choices=VIDEO_TYPES, default='video')
    is_preview = models.BooleanField(default=False, help_text="Available without enrollment")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['section__order', 'order']
    
    def __str__(self):
        return self.title
    
    def get_duration_display(self):
        """Convert seconds to minutes:seconds format"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"
    
    def get_youtube_id(self):
        """Extract YouTube ID from URL"""
        import re
        if self.video_url and ('youtube.com' in self.video_url or 'youtu.be' in self.video_url):
            match = re.search(r'(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/\\s]{11})', self.video_url)
            if match:
                return match.group(1)
        return None

# NEW: Enrollment Model
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress = models.FloatField(default=0.0)  # Percentage completion
    
    class Meta:
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

# NEW: Video Progress Tracking
class VideoProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_duration = models.IntegerField(default=0)  # Seconds watched
    is_completed = models.BooleanField(default=False)
    last_watched = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'video']
    
    def __str__(self):
        return f"{self.user.username} - {self.video.title}"

# LEGACY: Original Course Model (for backward compatibility)
class LegacyCourse(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="legacy_courses")
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Not Started")
    completion_percentage = models.PositiveIntegerField(default=0)
    deadline = models.DateField(null=True, blank=True)
    start_date = models.DateField(default=timezone.now)
    hours_spent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.student.username}"

class Quiz(models.Model):
    course = models.ForeignKey('LegacyCourse', on_delete=models.CASCADE)  # Updated to LegacyCourse
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    course = models.ForeignKey('LegacyCourse', on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)  # Updated to LegacyCourse
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.student.username})"

class QuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    attempted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

class StudyHabit(models.Model):
    HABIT_CATEGORIES = [
        ('time_management', 'Time Management'),
        ('focus', 'Focus & Concentration'),
        ('health', 'Health & Wellness'),
        ('learning', 'Learning Techniques'),
    ]
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="study_habits")
    habit_name = models.CharField(max_length=100)
    habit_category = models.CharField(max_length=50, choices=HABIT_CATEGORIES)
    target_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    current_streak = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.habit_name} - {self.student.username}"

class StudySession(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="study_sessions")
    course = models.ForeignKey('LegacyCourse', on_delete=models.CASCADE, null=True, blank=True)  # Updated to LegacyCourse
    duration_minutes = models.IntegerField()
    focus_score = models.IntegerField(default=5)
    productivity_score = models.IntegerField(default=5)
    session_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.duration_minutes}min - {self.session_date}"

class StudentGoal(models.Model):
    GOAL_TYPES = [
        ('study_hours', 'Study Hours'),
        ('habit_streak', 'Habit Streak'),
        ('course_completion', 'Course Completion'),
        ('grade_target', 'Grade Target'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    goal_text = models.TextField()
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPES)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.goal_text} - {self.student.username}"

class HabitNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('study_reminder', 'Study Reminder'),
        ('progress_alert', 'Progress Alert'), 
        ('goal_reminder', 'Goal Reminder'),
        ('deadline_alert', 'Deadline Alert'),
        ('study_tip', 'Study Tip'),
        ('course_completion', 'Course Completion'),
        ('quiz_reminder', 'Quiz Reminder'),
        ('high_completion_alert', 'High Completion Alert')
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_course = models.ForeignKey('LegacyCourse', on_delete=models.CASCADE, null=True, blank=True)  # Updated to LegacyCourse
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    scheduled_time = models.TimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.student.username}"

    class Meta:
        ordering = ['-created_at']