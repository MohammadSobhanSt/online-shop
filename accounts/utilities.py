from random import randint
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from accounts.models import Confirm


def send_otp_email(request):
    otp = randint(100000, 999999)

    Confirm.objects.create(user=request.user, otp=otp)

    subject = "Confirmation OTP"
    message = f"""Hello dear {request.user.username},
    Your OTP code for email verification is: {otp}.
    This code will expire in 10 minutes.
    If you didn't request this, please ignore this email.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [request.user.email]

    try:
        send_mail(
            subject,
            message,
            from_email,
            to_email,
            fail_silently=False)

        messages.info(request, "A new OTP has been sent to your email.", "info")
        return True

    except Exception as e:
        messages.error(request, f"Failed to send email: {str(e)}", "danger")
        return False