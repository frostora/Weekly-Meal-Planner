# this script is to manage email sends

from django.core.mail import send_mail
from django.conf import settings

def send_email(name, email, msg):
    if not name:
        name = "Anonymous"
    if not email:
        email = "Email Not Given"
    subject = "Feedback for Weekly Meal Planner"
    message = f"Message from {name} ({email}):\n\n{msg}"
    from_email = settings.EMAIL_HOST_USER  # your gmail
    to_email = [settings.EMAIL_HOST_USER]  # send to yourself

    
    result = send_mail(subject, message, from_email, to_email)
    if(result):
        return 1
    else:
        return 0