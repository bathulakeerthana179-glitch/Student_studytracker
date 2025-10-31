import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Studytrack.settings')
django.setup()

from django.core.mail import send_mail

print("🚀 Testing StudyTrack Email System...")

try:
    send_mail(
        '🎯 StudyTrack Test Email - SUCCESS!',
        '''Congratulations! Your StudyTrack email system is working perfectly! 🚀

You will now receive:
• AI-powered study reminders
• Course completion alerts  
• Quiz notifications
• Daily motivation messages

This is a real email sent from your Django application!''',
        'studytrackerai@gmail.com',
        ['studytrackerai@gmail.com'],  # Send to yourself
        fail_silently=False,
    )
    print("✅ TEST EMAIL SENT SUCCESSFULLY!")
    print("📧 Check your Gmail inbox NOW!")
    
except Exception as e:
    print(f"❌ EMAIL FAILED: {e}")
    print("💡 Check your Gmail app password in settings.py")