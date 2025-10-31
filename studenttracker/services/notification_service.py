from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta

class StudyHabitNotificationService:
    def __init__(self):
        pass
    
    def _get_student_context(self, user):
        """Get context data for student notifications"""
        try:
            # Use basic user data that exists in your database
            return {
                'student_name': user.get_full_name() or user.username,
                'current_date': timezone.now().strftime("%B %d, %Y"),
                'pending_assignments': 0,  # Default value
                'upcoming_deadlines': [],  # Default value
                'study_hours_today': 0,    # Default value
                'target_hours': 4,         # Default value
                'completed_courses': 0,    # Default value
                'total_courses': 0,        # Default value
                'progress_percentage': 0,  # Default value
            }
            
        except Exception as e:
            print(f"Error getting student context: {e}")
            # Return fallback data
            return {
                'student_name': user.get_full_name() or user.username,
                'current_date': timezone.now().strftime("%B %d, %Y"),
                'pending_assignments': 0,
                'upcoming_deadlines': [],
                'study_hours_today': 0,
                'target_hours': 4,
                'completed_courses': 0,
                'total_courses': 0,
                'progress_percentage': 0,
            }
    
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
    
    def send_study_reminders(self):
        """Send study habit reminders"""
        try:
            from studenttracker.models import User
            users = User.objects.filter(is_active=True)
            
            success_count = 0
            for user in users:
                if user.email:
                    context = self._get_student_context(user)
                    
                    # Determine time-based subject
                    current_hour = timezone.now().hour
                    if current_hour < 12:
                        time_greeting = "Morning"
                    elif current_hour < 17:
                        time_greeting = "Afternoon"
                    else:
                        time_greeting = "Evening"
                    
                    sent = self._send_email(
                        subject=f"📚 {time_greeting} Study Reminder - {timezone.now().strftime('%Y-%m-%d')}",
                        template_name="emails/study_reminder.html",
                        context=context,
                        recipient_list=[user.email]
                    )
                    
                    if sent:
                        success_count += 1
                        print(f"✅ Study reminder sent to {user.email}")
                    else:
                        print(f"❌ Failed to send study reminder to {user.email}")
            
            print(f"🎯 Study reminders completed: {success_count}/{len(users)} sent successfully!")
            return success_count
            
        except Exception as e:
            print(f"❌ Error sending study reminders: {e}")
            return 0

    def send_test_notification(self):
        """Send test notification"""
        try:
            from studenttracker.models import User
            # Get first active user or use admin
            user = User.objects.filter(is_active=True).first()
            if not user:
                # Create test context if no users
                test_context = {
                    'student_name': 'Test User',
                    'current_date': timezone.now().strftime("%B %d, %Y"),
                    'pending_assignments': 2,
                    'upcoming_deadlines': ['Test Assignment - Tomorrow'],
                    'study_hours_today': 1,
                    'target_hours': 4,
                    'completed_courses': 3,
                    'total_courses': 8,
                    'progress_percentage': 37.5,
                }
                recipient = [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@example.com']
            else:
                test_context = self._get_student_context(user)
                recipient = [user.email]
            
            sent = self._send_email(
                subject="🧪 Test Notification - Study Tracker",
                template_name="emails/study_reminder.html",
                context=test_context,
                recipient_list=recipient
            )
            
            if sent:
                print("✅ Test notification sent successfully!")
            else:
                print("❌ Failed to send test notification")
                
            return sent
            
        except Exception as e:
            print(f"❌ Test notification error: {e}")
            return False

    def send_morning_reminder(self, user=None):
        """Send morning reminder notifications"""
        try:
            from studenttracker.models import User
            if user:
                users = [user]
            else:
                users = User.objects.filter(is_active=True)
            
            success_count = 0
            for user_obj in users:
                if user_obj.email:
                    context = self._get_student_context(user_obj)
                    
                    sent = self._send_email(
                        subject="🌅 Morning Study Reminder - Start Your Day Right!",
                        template_name="emails/study_reminder.html",
                        context=context,
                        recipient_list=[user_obj.email]
                    )
                    
                    if sent:
                        success_count += 1
                        print(f"✅ Morning reminder sent to {user_obj.email}")
            
            print(f"🎯 Morning reminders: {success_count}/{len(users)} sent successfully!")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error sending morning reminder: {e}")
            return False

    def send_afternoon_checkin(self, user=None):
        """Send afternoon check-in notifications"""
        try:
            from studenttracker.models import User
            if user:
                users = [user]
            else:
                users = User.objects.filter(is_active=True)
            
            success_count = 0
            for user_obj in users:
                if user_obj.email:
                    context = self._get_student_context(user_obj)
                    
                    sent = self._send_email(
                        subject="☀️ Afternoon Study Check-in - Keep Going!",
                        template_name="emails/study_reminder.html", 
                        context=context,
                        recipient_list=[user_obj.email]
                    )
                    
                    if sent:
                        success_count += 1
                        print(f"✅ Afternoon check-in sent to {user_obj.email}")
            
            print(f"🎯 Afternoon check-ins: {success_count}/{len(users)} sent successfully!")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error sending afternoon check-in: {e}")
            return False

    def send_evening_review(self, user=None):
        """Send evening review notifications"""
        try:
            from studenttracker.models import User
            if user:
                users = [user]
            else:
                users = User.objects.filter(is_active=True)
            
            success_count = 0
            for user_obj in users:
                if user_obj.email:
                    context = self._get_student_context(user_obj)
                    
                    sent = self._send_email(
                        subject="🌙 Evening Study Review - Great Work Today!",
                        template_name="emails/study_reminder.html",
                        context=context,
                        recipient_list=[user_obj.email]
                    )
                    
                    if sent:
                        success_count += 1
                        print(f"✅ Evening review sent to {user_obj.email}")
            
            print(f"🎯 Evening reviews: {success_count}/{len(users)} sent successfully!")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error sending evening review: {e}")
            return False

    def send_night_motivation(self, user=None):
        """Send night motivation notifications"""
        try:
            from studenttracker.models import User
            if user:
                users = [user]
            else:
                users = User.objects.filter(is_active=True)
            
            success_count = 0
            for user_obj in users:
                if user_obj.email:
                    context = self._get_student_context(user_obj)
                    
                    sent = self._send_email(
                        subject="🌌 Night Motivation - Plan for Tomorrow!",
                        template_name="emails/study_reminder.html",
                        context=context,
                        recipient_list=[user_obj.email]
                    )
                    
                    if sent:
                        success_count += 1
                        print(f"✅ Night motivation sent to {user_obj.email}")
            
            print(f"🎯 Night motivations: {success_count}/{len(users)} sent successfully!")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error sending night motivation: {e}")
            return False