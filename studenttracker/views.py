from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.utils import timezone
import re
from .models import User, Course, Task, HabitNotification, VideoSection, Video, Enrollment, VideoProgress
from .services.notification_service import StudyHabitNotificationService

# -------------------------------------------
# HOME PAGE
# -------------------------------------------
def home(request):
    return render(request, 'studenttracker/home.html')

# -------------------------------------------
# REGISTER USER
# -------------------------------------------
def register_user(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm', '')
        education = request.POST.get('education', '').strip()

        # Validation
        if not all([first_name, last_name, email, password, confirm]):
            messages.error(request, "⚠ Please fill all required fields.")
            return render(request, 'studenttracker/register.html')
        
        if password != confirm:
            messages.error(request, "⚠ Passwords do not match.")
            return render(request, 'studenttracker/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "⚠ Email already registered.")
            return render(request, 'studenttracker/register.html')

        try:
            # USE Django's create_user method which properly hashes passwords
            user = User.objects.create_user(
                username=email,  # Use email as username
                email=email,
                password=password,  # Django will hash this automatically
                first_name=first_name,
                last_name=last_name,
                education=education,
                role="student"
            )
            messages.success(request, "✅ Registration successful! Please login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"⚠ Registration failed: {str(e)}")
            return render(request, 'studenttracker/register.html')

    return render(request, 'studenttracker/register.html')

# -------------------------------------------
# LOGIN USER
# -------------------------------------------
def login_user(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        try:
            # Find user by email (since we use email as username)
            user = User.objects.get(email=email)
            # Authenticate using Django's system
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"✅ Welcome back, {user.first_name}!")
                
                if user.role == "admin":
                    return redirect('admin_dashboard')
                else:
                    return redirect('dashboard')
            else:
                messages.error(request, "⚠ Invalid email or password")
        except User.DoesNotExist:
            messages.error(request, "⚠ Invalid email or password")
    
    return render(request, 'studenttracker/login.html')

# -------------------------------------------
# STUDENT DASHBOARD (UPDATED FOR VIDEO COURSES)
# -------------------------------------------
@login_required
def dashboard(request):
    user = request.user
    
    # Get enrolled courses with progress
    enrolled_courses = Enrollment.objects.filter(user=user).select_related('course')
    
    # Get active video for playing (if any)
    active_video = None
    video_id = request.GET.get('video_id')
    if video_id:
        try:
            active_video = Video.objects.get(id=video_id)
            # Check if user can access this video
            if not active_video.is_preview:
                enrollment = Enrollment.objects.filter(user=user, course=active_video.section.course).first()
                if not enrollment:
                    messages.error(request, 'You need to enroll in this course to watch this video.')
                    return redirect('dashboard')
        except Video.DoesNotExist:
            pass
    
    # Get courses for continue learning (in progress)
    continue_learning_courses = []
    for enrollment in enrolled_courses.filter(progress__lt=100):
        # Find the next unwatched video
        next_video = Video.objects.filter(
            section__course=enrollment.course
        ).exclude(
            videoprogress__user=user, 
            videoprogress__is_completed=True
        ).first()
        
        if next_video:
            continue_learning_courses.append({
                'course': enrollment.course,
                'progress': enrollment.progress,
                'next_video': next_video
            })
    
    # Get high completion courses (75%+ complete)
    high_completion_courses = []
    for enrollment in enrolled_courses.filter(progress__gte=75, progress__lt=100):
        total_videos = Video.objects.filter(section__course=enrollment.course).count()
        completed_videos = VideoProgress.objects.filter(
            user=user, 
            video__section__course=enrollment.course, 
            is_completed=True
        ).count()
        
        high_completion_courses.append({
            'id': enrollment.course.id,
            'title': enrollment.course.title,
            'progress': enrollment.progress,
            'total_videos': total_videos,
            'completed_videos': completed_videos
        })
    
    # Get preview courses (with preview videos)
    preview_courses = Course.objects.filter(
        sections__videos__is_preview=True,
        is_published=True
    ).distinct()
    
    # Get preview courses with their preview videos
    preview_courses_with_videos = []
    for course in preview_courses:
        preview_videos = Video.objects.filter(
            section__course=course, 
            is_preview=True
        )[:3]  # Limit to 3 preview videos per course
        
        preview_courses_with_videos.append({
            'course': course,
            'preview_videos': preview_videos,
            'preview_videos_count': preview_videos.count()
        })
    
    # Legacy data for backward compatibility
    courses = Course.objects.filter(enrollments__user=user)
    tasks = Task.objects.filter(student=user)
    notifications = HabitNotification.objects.filter(student=user, is_read=False)
    
    context = {
        'user': user,
        'enrolled_courses': enrolled_courses,
        'active_video': active_video,
        'continue_learning_courses': continue_learning_courses,
        'high_completion_courses': high_completion_courses,
        'preview_courses': preview_courses,
        'preview_courses_with_videos': preview_courses_with_videos,
        'courses': courses,  # Legacy
        'tasks': tasks,      # Legacy
        'notifications': notifications.order_by('-created_at')[:10],
    }
    
    return render(request, 'studenttracker/dashboard.html', context)

# -------------------------------------------
# ADMIN DASHBOARD (UPDATED FOR VIDEO COURSES)
# -------------------------------------------
@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        messages.error(request, "⚠ You are not authorized to view this page.")
        return redirect('dashboard')

    # Handle form submissions for adding courses
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        name = request.POST.get('name')
        deadline = request.POST.get('deadline')
        status = request.POST.get('status', 'Not Started')
        
        if student_id and name and deadline:
            try:
                student = User.objects.get(id=student_id)
                Course.objects.create(
                    student=student, 
                    name=name, 
                    deadline=deadline,
                    status=status
                )
                messages.success(request, f"✅ Course '{name}' added for {student.first_name}!")
            except User.DoesNotExist:
                messages.error(request, "⚠ Student not found.")
        
        return redirect('admin_dashboard')

    students = User.objects.filter(role="student")

    return render(request, "studenttracker/admin_dashboard.html", {
        "admin_user": request.user,
        "students": students
    })

# -------------------------------------------
# ADD COURSE (Admin Only - UPDATED FOR VIDEO COURSES)
# -------------------------------------------
@login_required
def add_course(request):
    if request.user.role != "admin":
        messages.error(request, "⚠ Only admin can access this page.")
        return redirect('dashboard')

    students = User.objects.filter(role="student")

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        level = request.POST.get('level', 'beginner')
        price = request.POST.get('price', 0)
        duration_hours = request.POST.get('duration_hours', 10)
        is_published = 'is_published' in request.POST
        
        # Create course without instructor
        course = Course.objects.create(
            title=title,
            description=description,
            level=level,
            price=price,
            duration_hours=duration_hours,
            is_published=is_published
        )
        
        # Enroll selected students if checkbox is checked
        if 'enroll_students' in request.POST:
            student_ids = request.POST.getlist('students')
            if student_ids:
                for student_id in student_ids:
                    student = get_object_or_404(User, id=student_id)
                    Enrollment.objects.create(user=student, course=course)
        
        messages.success(request, f"✅ Course '{title}' created successfully!")
        return redirect('admin_dashboard')

    return render(request, 'studenttracker/add_course.html', {
        'students': students,
    })

# -------------------------------------------
# ADD VIDEO (Admin Only - UPDATED)
# -------------------------------------------
@login_required
def add_video(request):
    if request.user.role != "admin":
        messages.error(request, "⚠ Only admin can access this page.")
        return redirect('dashboard')

    courses = Course.objects.all()
    
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_url = request.POST.get('video_url')
        duration = request.POST.get('duration')
        order = request.POST.get('order', 0)
        video_type = request.POST.get('video_type', 'video')
        is_preview = 'is_preview' in request.POST
        
        course = get_object_or_404(Course, id=course_id)
        
        # Create or get a default section for the course
        default_section, created = VideoSection.objects.get_or_create(
            course=course,
            title="Main Content",
            defaults={'order': 0}
        )
        
        # Extract YouTube ID if it's a YouTube URL
        youtube_id = None
        if video_url and ('youtube.com' in video_url or 'youtu.be' in video_url):
            match = re.search(r'(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/\\s]{11})', video_url)
            if match:
                youtube_id = match.group(1)
        
        video = Video.objects.create(
            section=default_section,  # Use the default section
            title=title,
            description=description,
            video_url=video_url,
            duration=duration,
            order=order,
            video_type=video_type,
            is_preview=is_preview
        )
        
        messages.success(request, f"✅ Video '{title}' added successfully!")
        return redirect('admin_dashboard')
    
    context = {
        'courses': courses,
    }
    return render(request, 'studenttracker/add_video.html', context)

# -------------------------------------------
# ADD TASK (Admin Only)
# -------------------------------------------
@login_required
def add_task(request):
    if request.user.role != "admin":
        messages.error(request, "⚠ Only admin can access this page.")
        return redirect('dashboard')

    students = User.objects.filter(role="student")
    courses = Course.objects.all()

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        status = request.POST.get('status', 'Pending')

        if not all([student_id, course_id, title, deadline]):
            messages.error(request, "⚠ Please fill all required fields.")
            return redirect('add_task')

        student = get_object_or_404(User, id=student_id)
        course = get_object_or_404(Course, id=course_id)
        Task.objects.create(
            student=student,
            course=course,
            title=title,
            description=description,
            deadline=deadline,
            status=status
        )
        messages.success(request, f"✅ Task '{title}' assigned to {student.first_name}.")
        return redirect('admin_dashboard')

    return render(request, 'studenttracker/add_task.html', {
        'students': students, 
        'courses': courses
    })
# -------------------------------------------
# ENROLL IN COURSE
# -------------------------------------------
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if existing_enrollment:
        messages.info(request, f'You are already enrolled in "{course.title}"')
        return redirect('course_detail', course_id=course_id)
    
    # Create enrollment
    Enrollment.objects.create(user=request.user, course=course)
    
    # Update course students count
    course.students_count = Enrollment.objects.filter(course=course).count()
    course.save()
    
    messages.success(request, f'✅ Successfully enrolled in "{course.title}"!')
    return redirect('course_detail', course_id=course_id)
# -------------------------------------------
# VIDEO PLAYBACK VIEWS (UPDATED)
# -------------------------------------------
@login_required
def play_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    # Check if user is enrolled or video is preview
    if not video.is_preview:
        enrollment = Enrollment.objects.filter(
            user=request.user, 
            course=video.section.course
        ).first()
        if not enrollment:
            messages.error(request, 'You need to enroll in this course to watch this video.')
            return redirect('dashboard')
    
    # Update or create video progress
    progress, created = VideoProgress.objects.get_or_create(
        user=request.user,
        video=video,
        defaults={'watched_duration': 0, 'is_completed': False}
    )
    
    # Redirect to dashboard with video parameter to show the player
    return redirect(f'/dashboard/?video_id={video_id}')

@login_required
def mark_video_completed(request, video_id):
    if request.method == 'POST':
        video = get_object_or_404(Video, id=video_id)
        
        # Update progress
        progress, created = VideoProgress.objects.get_or_create(
            user=request.user,
            video=video
        )
        progress.is_completed = True
        progress.watched_duration = video.duration  # Assume full duration watched
        progress.save()
        
        # Update course progress
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=video.section.course
        ).first()
        
        if enrollment:
            # Calculate new progress
            total_videos = Video.objects.filter(section__course=enrollment.course).count()
            completed_videos = VideoProgress.objects.filter(
                user=request.user,
                video__section__course=enrollment.course,
                is_completed=True
            ).count()
            
            enrollment.progress = (completed_videos / total_videos) * 100 if total_videos > 0 else 0
            enrollment.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def video_notes(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    # Implement notes functionality here
    return render(request, 'studenttracker/video_notes.html', {'video': video})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    
    if not enrollment and not course.sections.filter(videos__is_preview=True).exists():
        messages.error(request, 'You need to enroll in this course to access it.')
        return redirect('dashboard')
    
    context = {
        'course': course,
        'enrollment': enrollment,
    }
    return render(request, 'studenttracker/course_detail.html', context)

# -------------------------------------------
# NOTIFICATION VIEWS
# -------------------------------------------
@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = HabitNotification.objects.get(id=notification_id, student=request.user)
        notification.is_read = True
        notification.save()
        print(f"✅ Marked notification {notification_id} as read for user {request.user.email}")
        return JsonResponse({'success': True})
    except HabitNotification.DoesNotExist:
        print(f"❌ Notification {notification_id} not found for user {request.user.email}")
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@login_required
def test_study_reminder(request):
    """Test study reminder (for development)"""
    notification_service = StudyHabitNotificationService()
    success = notification_service.send_study_reminder(request.user)
    return JsonResponse({'success': success})

# -------------------------------------------
# LOGOUT
# -------------------------------------------
def logout_user(request):
    logout(request)
    messages.info(request, "👋 You have been logged out successfully.")
    return redirect('home')