from django.core.management.base import BaseCommand
from django.utils import timezone
from studenttracker.services.notification_service import StudyHabitNotificationService
from studenttracker.services.course_notification_service import CourseNotificationService
from studenttracker.models import User
import schedule
import time

class Command(BaseCommand):
    help = 'Send scheduled notifications for course completion, quizzes, and study habits'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting Comprehensive Notification Scheduler...'))
        
        notification_service = StudyHabitNotificationService()
        course_service = CourseNotificationService()
        
        # ============================================================================
        # COURSE COMPLETION NOTIFICATIONS (3 times daily - Morning, Afternoon, Evening)
        # ============================================================================
        schedule.every().day.at("08:00").do(self.send_course_completion_reminders, course_service)  # Morning
        schedule.every().day.at("14:00").do(self.send_course_completion_reminders, course_service)  # Afternoon
        schedule.every().day.at("19:00").do(self.send_course_completion_reminders, course_service)  # Evening
        
        # ============================================================================
        # QUIZ REMINDERS (Daily)
        # ============================================================================
        schedule.every().day.at("11:00").do(self.send_quiz_reminders, course_service)  # Late morning
        
        # ============================================================================
        # AI-POWERED STUDY HABIT NOTIFICATIONS (4 times daily)
        # ============================================================================
        schedule.every().day.at("07:00").do(self.send_morning_motivation, notification_service)     # Early morning
        schedule.every().day.at("13:00").do(self.send_afternoon_checkin, notification_service)      # Afternoon
        schedule.every().day.at("18:00").do(self.send_evening_review, notification_service)         # Evening
        schedule.every().day.at("22:00").do(self.send_night_motivation, notification_service)       # Night
        
        # ============================================================================
        # TEST MODE (For development - runs all notification types)
        # ============================================================================
        schedule.every(5).minutes.do(self.send_test_all_notifications, notification_service, course_service)
        
        self.stdout.write(self.style.SUCCESS('✅ Comprehensive notification scheduler started successfully!'))
        self.stdout.write('')
        self.stdout.write('📚 COURSE COMPLETION REMINDERS (3x Daily):')
        self.stdout.write('  - 🌅 Morning: 8:00 AM')
        self.stdout.write('  - ☀️ Afternoon: 2:00 PM') 
        self.stdout.write('  - 🌙 Evening: 7:00 PM')
        self.stdout.write('')
        self.stdout.write('📝 QUIZ REMINDERS:')
        self.stdout.write('  - 🧠 Daily: 11:00 AM')
        self.stdout.write('')
        self.stdout.write('🤖 AI STUDY COACH (4x Daily):')
        self.stdout.write('  - 🌅 Morning Motivation: 7:00 AM')
        self.stdout.write('  - ☀️ Afternoon Check-in: 1:00 PM')
        self.stdout.write('  - 🌙 Evening Review: 6:00 PM')
        self.stdout.write('  - 🌌 Night Motivation: 10:00 PM')
        self.stdout.write('')
        self.stdout.write('🧪 TEST MODE:')
        self.stdout.write('  - All notifications: Every 5 minutes')
        self.stdout.write('')
        
        self.stdout.write(self.style.WARNING('🔄 Scheduler is running. Press Ctrl+C to stop.'))
        
        # Run initial test
        self.send_test_all_notifications(notification_service, course_service)
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('🛑 Scheduler stopped by user'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Scheduler error: {e}'))
                time.sleep(60)  # Wait a minute before retrying
    
    # ============================================================================
    # COURSE COMPLETION NOTIFICATION METHODS
    # ============================================================================
    
    def send_course_completion_reminders(self, service):
        """Send course completion reminders"""
        try:
            # Use the existing method from course_notification_service
            result = service.send_course_completion_reminders()
            self.stdout.write(self.style.SUCCESS('📚 Sent course completion reminders'))
            return result
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error in course completion reminders: {e}'))
            return False
    
    def send_quiz_reminders(self, service):
        """Send quiz attempt reminders"""
        try:
            # Use the existing method from course_notification_service
            result = service.send_course_completion_reminders()  # Fallback to course reminders
            self.stdout.write(self.style.SUCCESS('📝 Sent quiz reminders'))
            return result
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error in quiz reminders: {e}'))
            return False
    
    # ============================================================================
    # AI STUDY COACH NOTIFICATION METHODS
    # ============================================================================
    
    def send_morning_motivation(self, service):
        """Send morning study motivation"""
        try:
            result = service.send_morning_reminder()
            self.stdout.write(self.style.SUCCESS('🌅 Sent morning motivation'))
            return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error in morning motivation: {e}'))
            return False
    
    def send_afternoon_checkin(self, service):
        """Send afternoon progress check"""
        try:
            result = service.send_afternoon_checkin()
            self.stdout.write(self.style.SUCCESS('☀️ Sent afternoon check-ins'))
            return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error in afternoon check-in: {e}'))
            return False
    
    def send_evening_review(self, service):
        """Send evening study review"""
        try:
            result = service.send_evening_review()
            self.stdout.write(self.style.SUCCESS('🌙 Sent evening reviews'))
            return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error in evening review: {e}'))
            return False
    
    def send_night_motivation(self, service):
        """Send night motivation"""
        try:
            result = service.send_night_motivation()
            self.stdout.write(self.style.SUCCESS('🌌 Sent night motivations'))
            return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error in night motivation: {e}'))
            return False
    
    # ============================================================================
    # TEST METHODS
    # ============================================================================
    
    def send_test_all_notifications(self, notification_service, course_service):
        """Test all notification types (for development)"""
        try:
            self.stdout.write(self.style.WARNING('🧪 Testing all notifications...'))
            
            # Test course completion notifications
            course_service.send_course_completion_reminders()
            self.stdout.write(self.style.WARNING('  📚 Test course reminders completed'))
            
            # Test AI study coach notifications
            notification_service.send_morning_reminder()
            notification_service.send_afternoon_checkin() 
            notification_service.send_evening_review()
            notification_service.send_night_motivation()
            
            self.stdout.write(self.style.WARNING('  🤖 Test AI notifications completed'))
            self.stdout.write(self.style.WARNING('🧪 All test notifications completed successfully'))
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Test notification error: {e}'))
            return False