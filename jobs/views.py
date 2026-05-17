from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMessage
import logging
from threading import Thread
from typing import Optional
from .models import Job, Company, GeneralApplication, ContactMessage

logger = logging.getLogger(__name__)


def _send_brevo_email(
    *,
    subject: str,
    body: str,
    to_email: str,
    reply_to: Optional[str] = None,
    attachments: Optional[list[dict]] = None,
) -> None:
    """Send an email via Brevo using Django's SMTP backend."""
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            reply_to=[reply_to] if reply_to else None,
        )

        if attachments:
            for attachment in attachments:
                email.attach(
                    attachment.get('filename', 'attachment'),
                    attachment.get('content', b''),
                    attachment.get('type', 'application/octet-stream'),
                )

        email.send()
    except Exception as e:
        raise RuntimeError(f'Brevo email send failed: {str(e)}') from e


def _send_contact_email(name: str, email: str, subject: str, message: str) -> None:
    """Send contact email in background to avoid blocking HTTP response."""
    try:
        _send_brevo_email(
            subject=subject or f'Contact inquiry from {name}',
            body=(
                f'Name: {name}\n'
                f'Email: {email}\n'
                f'Subject: {subject or "General Inquiry"}\n\n'
                f'Message:\n{message}\n'
            ),
            to_email=settings.GENERAL_APPLICATION_RECIPIENT,
            reply_to=email,
        )
    except Exception as e:
        logger.error(f"Contact email send failed: {str(e)}")

CONTACT_INFO = {
    'address': 'Plot 48, Itam Industrial Layout, Uyo, Akwa Ibom State, Nigeria',
    'email': 'inquiry@goshengiantgroup.com',
    'phone': '+234 705 702 5093',
}


def careers(request):
    """Main careers page with all sections"""
    jobs = Job.objects.all()
    companies = Company.objects.all()
    
    context = {
        'jobs': jobs,
        'companies': companies,
        'total_jobs': jobs.count(),
        'join_widget_embed_code': getattr(settings, 'JOIN_WIDGET_EMBED_CODE', ''),
        'join_careers_url': getattr(settings, 'JOIN_CAREERS_URL', ''),
    }
    return render(request, 'jobs/careers.html', context)


def about(request):
    """About page for Goshen Giant Food Limited."""
    return render(request, 'jobs/about.html')


@require_http_methods(["GET", "POST"])
def contact(request):
    """Contact page with company details and inquiry form."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not message:
            messages.error(request, 'Please fill in your name, email, and message.')
            return render(request, 'jobs/contact.html', {'contact_info': CONTACT_INFO})

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        Thread(
            target=_send_contact_email,
            args=(name, email, subject, message),
            daemon=True,
        ).start()

        messages.success(request, "Thanks - your message has been received. We'll get back to you shortly.")
        return redirect('contact')

    return render(request, 'jobs/contact.html', {'contact_info': CONTACT_INFO})


def job_detail(request, pk):
    """Show a local detail page for a JOIN-synced job."""
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'jobs/job_detail.html', {'job': job})


@require_http_methods(["GET", "POST"])
def general_application(request):
    """Handle general job applications"""
    selected_job = None
    job_id = request.GET.get('job')
    if job_id:
        selected_job = Job.objects.filter(pk=job_id).first()

    if request.method == 'POST':
        experience_value = request.POST.get('experience_years', '').strip()
        try:
            experience_years = int(experience_value) if experience_value else 0
        except ValueError:
            experience_years = 0

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        cover_letter = request.POST.get('cover_letter', '').strip()
        skills = request.POST.get('skills', '').strip()
        extra_details = request.POST.get('extra_details', '').strip()
        custom_position = request.POST.get('position_applied', '').strip()
        resume_file = request.FILES.get('resume')
        posted_job_id = request.POST.get('job_id')
        if posted_job_id:
            selected_job = Job.objects.filter(pk=posted_job_id).first()

        position_applied = selected_job.title if selected_job else custom_position

        if not position_applied:
            messages.error(request, 'Please specify the position you are applying for.')
            return render(request, 'jobs/general_application.html', {'selected_job': selected_job})

        if not resume_file:
            messages.error(request, 'Please attach your resume before submitting.')
            return render(request, 'jobs/general_application.html')

        # Keep resume in-memory for email attachment only.
        resume_bytes = resume_file.read()
        resume_file.seek(0)

        application = GeneralApplication(
            job=selected_job,
            position_applied=position_applied,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            resume=resume_file,
            cover_letter=cover_letter,
            skills=skills,
            experience_years=experience_years,
        )
        application.save()

        subject = f"Application for {position_applied} - {first_name} {last_name}".strip()
        body = (
            "A new general application was submitted.\n\n"
            f"Position Applied For: {position_applied}\n"
            f"First Name: {first_name}\n"
            f"Last Name: {last_name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Years of Experience: {experience_years}\n"
            f"Skills: {skills or 'N/A'}\n"
            f"Cover Letter:\n{cover_letter or 'N/A'}\n\n"
            f"Other Important Details:\n{extra_details or 'N/A'}\n"
        )

        try:
            _send_brevo_email(
                subject=subject,
                body=body,
                to_email=settings.GENERAL_APPLICATION_RECIPIENT,
                reply_to=email if email else None,
                attachments=[
                    {
                        'content': resume_bytes,
                        'type': resume_file.content_type or 'application/octet-stream',
                        'filename': resume_file.name,
                    }
                ],
            )
            messages.success(request, 'Thank you! Your application has been submitted and emailed successfully.')
        except Exception as e:
            logger.error(f"Email send failed: {str(e)}")
            messages.warning(request, 'Application email delivery failed. Please check email settings.')

        return redirect('careers')
    
    return render(request, 'jobs/general_application.html', {'selected_job': selected_job})


@require_http_methods(["GET", "POST"])
def job_application(request, pk):
    """Legacy route: redirect to the general application form with selected position."""
    get_object_or_404(Job, pk=pk)
    return redirect(f"{reverse('general_application')}?job={pk}")
