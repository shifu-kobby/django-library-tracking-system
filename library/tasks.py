from celery import shared_task
from django.utils import timezone

from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass


@shared_task(
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True
)
def check_overdue_loans():
    loans = Loan.objects.selected_related("book", "member__user").filter(
        is_returned=False,
        due_date__lte=timezone.now().date()
    )

    for loan in loans:
        member_email = loan.member.user.email
        book_title = loan.book.title

        try:
            send_mail(
                subject="Overdue Loan Notification",
                message=f'Hello {member_email},\n\n'
                        f'You have an overdue loan for {book_title} on {loan.due_date}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member_email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f'An error occurred when sending overdue mail for {member_email} for {book_title}. Details: {str(e)}')
