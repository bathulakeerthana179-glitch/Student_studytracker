from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

class CourseNotificationService:
    def __init__(self):
        pass
    
    def _send_email(self, subject, template_name, context, recipient_list):
        """Generic email sending method"""
        try:
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Email sending error: {e}")
            return False
    
    def _get_course_context(self, user):
        """Get context data for course notifications"""
        try:
            # Use basic user data that exists
            return {
                'student_name': user.get_full_name() or user.username,
                'current_date': timezone.now().strftime("%B %d, %Y"),
                'completed_courses': 0,  # Default value
                'total_courses': 0,      # Default value
                'progress_percentage': 0, # Default value
                'recent_courses': [],    # Default value
                'next_recommended_course': 'Start your first course!', # Default value
            }
            
        except Exception as e:
            print(f"Error getting course context: {e}")
            # Return fallback data
            return {
                'student_name': user.get_full_name() or user.username,
                'current_date': timezone.now().strftime("%B %d, %Y"),
                'completed_courses': 0,
                'total_courses': 0,
                'progress_percentage': 0,
                'recent_courses': [],
                'next_recommended_course': 'No courses enrolled',
            }
    
    def send_course_completion_reminders(self):
        """Send course completion reminders"""
        try:
            from studenttracker.models import User
            users = User.objects.filter(is_active=True)
            
            success_count = 0
            for user in users:
                if user.email:
                    context = self._get_course_context(user)
                    
                    # Determine time-based subject
                    current_hour = timezone.now().hour
                    if current_hour < 12:
                        time_greeting = "Morning"
                    elif current_hour < 17:
                        time_greeting = "Afternoon"
                    else:
                        time_greeting = "Evening"
                    
                    sent = self._send_email(
                        subject=f"🎓 {time_greeting} Course Update - {timezone.now().strftime('%Y-%m-%d')}",
                        template_name="emails/course_reminder.html",
                        context=context,
                        recipient_list=[user.email]
                    )
                    
                    if sent:
                        success_count += 1
                        print(f"✅ Course reminder sent to {user.email}")
                    else:
                        print(f"❌ Failed to send course reminder to {user.email}")
            
            print(f"🎯 Course reminders completed: {success_count}/{len(users)} sent successfully!")
            return success_count
            
        except Exception as e:
            print(f"❌ Error sending course reminders: {e}")
            return 0

    def send_course_test_notification(self):
        """Send test course notification"""
        try:
            from studenttracker.models import User
            # Get first active user or use admin
            user = User.objects.filter(is_active=True).first()
            if not user:
                # Create test context if no users
                test_context = {
                    'student_name': 'Test User',
                    'current_date': timezone.now().strftime("%B %d, %Y"),
                    'completed_courses': 3,
                    'total_courses': 8,
                    'progress_percentage': 37.5,
                    'recent_courses': ['Mathematics', 'Science', 'History'],
                    'next_recommended_course': 'Advanced Programming',
                }
                recipient = [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@example.com']
            else:
                test_context = self._get_course_context(user)
                recipient = [user.email]
            
            sent = self._send_email(
                subject="🧪 Test Course Notification - Study Tracker",
                template_name="emails/course_reminder.html",
                context=test_context,
                recipient_list=recipient
            )
            
            if sent:
                print("✅ Test course notification sent successfully!")
            else:
                print("❌ Failed to send test course notification")
                
            return sent
            
        except Exception as e:
            print(f"❌ Test course notification error: {e}")
            return False