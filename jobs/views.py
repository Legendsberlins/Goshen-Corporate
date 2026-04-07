from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse
import logging
from .models import Job, Company, GeneralApplication

logger = logging.getLogger(__name__)


def careers(request):
    """Main careers page with all sections"""
    jobs = Job.objects.all()
    companies = Company.objects.all()
    
    context = {
        'jobs': jobs,
        'companies': companies,
        'total_jobs': jobs.count(),
    }
    return render(request, 'jobs/careers.html', context)


def about(request):
    """About page for Goshen Giant Food Limited."""
    return render(request, 'jobs/about.html')


def job_detail(request, pk):
    """Redirect to join.com job posting"""
    job = get_object_or_404(Job, pk=pk)
    if job.join_com_url:
        return redirect(job.join_com_url)
    # If no join.com URL, redirect back to careers page
    return redirect('careers')


@require_http_methods(["GET", "POST"])
def general_application(request):
    """Handle general job applications"""
    selected_job = None
    job_id = request.GET.get('job')
    if job_id:
        selected_job = Job.objects.filter(pk=job_id).first()
        # Redirect to join.com if URL is available
        if selected_job and selected_job.join_com_url:
            return redirect(selected_job.join_com_url)

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

        mail = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.GENERAL_APPLICATION_RECIPIENT],
            reply_to=[email] if email else None,
        )
        mail.attach(
            resume_file.name,
            resume_bytes,
            resume_file.content_type or 'application/octet-stream',
        )

        try:
            mail.send(fail_silently=False)
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
