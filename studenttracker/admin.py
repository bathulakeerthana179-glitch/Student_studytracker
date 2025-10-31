from django.contrib import admin
from .models import (
    User, LegacyCourse, Quiz, Task, QuizAttempt, StudyHabit, 
    StudySession, StudentGoal, HabitNotification,
    Course, VideoSection, Video, Enrollment, VideoProgress
)

# YouTube-style Models
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title',  'level', 'price', 'students_count', 'is_published', 'created_at']
    list_filter = ['level', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['students_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'thumbnail', 'instructor')
        }),
        ('Course Details', {
            'fields': ('level', 'price', 'duration_hours')
        }),
        ('Status', {
            'fields': ('is_published', 'students_count', 'rating')
        }),
    )

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ['title', 'video_url', 'duration', 'order', 'is_preview']

@admin.register(VideoSection)
class VideoSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'course__title']
    inlines = [VideoInline]
    ordering = ['course', 'order']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'video_type', 'duration', 'order', 'is_preview']
    list_filter = ['video_type', 'is_preview', 'section__course']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('section', 'title', 'description', 'video_type')
        }),
        ('Video Content', {
            'fields': ('video_url', 'video_file', 'thumbnail', 'duration')
        }),
        ('Settings', {
            'fields': ('order', 'is_preview')
        })
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'progress', 'completed_at']
    list_filter = ['enrolled_at', 'completed_at']
    search_fields = ['user__username', 'course__title']
    readonly_fields = ['enrolled_at']

@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'watched_duration', 'is_completed', 'last_watched']
    list_filter = ['is_completed', 'last_watched']
    search_fields = ['user__username', 'video__title']
    readonly_fields = ['last_watched']

# Legacy Models (Your existing models)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'education', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']

@admin.register(LegacyCourse)
class LegacyCourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'student', 'status', 'completion_percentage', 'deadline']
    list_filter = ['status', 'start_date']
    search_fields = ['name', 'student__username']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'course', 'status', 'deadline']
    list_filter = ['status', 'deadline']
    search_fields = ['title', 'student__username']

@admin.register(HabitNotification)
class HabitNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'student__username']
    readonly_fields = ['created_at']

# Register other legacy models without custom admin
admin.site.register(Quiz)
admin.site.register(QuizAttempt)
admin.site.register(StudyHabit)
admin.site.register(StudySession)
admin.site.register(StudentGoal)