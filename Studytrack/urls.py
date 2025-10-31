from django.contrib import admin
from django.urls import path
from studenttracker import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Course & Task Management (Admin only)
    path('add_course/', views.add_course, name='add_course'),
    path('add_video/', views.add_video, name='add_video'),
    path('add_task/', views.add_task, name='add_task'),

    # Video Management & Playback
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('video/play/<int:video_id>/', views.play_video, name='play_video'),
    path('video/<int:video_id>/mark-completed/', views.mark_video_completed, name='mark_video_completed'),
    path('video/<int:video_id>/notes/', views.video_notes, name='video_notes'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    
    # Notifications
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/test-reminder/', views.test_study_reminder, name='test_study_reminder'),
    
    # Temporary redirects
    path('courses/', views.dashboard, name='courses'),
    path('tasks/', views.dashboard, name='tasks'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
