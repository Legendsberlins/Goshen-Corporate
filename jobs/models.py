from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Companies'
    
    def __str__(self):
        return self.name


class Job(models.Model):
    LOCATION_CHOICES = [
        ('uyo', 'Uyo'),
        ('abuja', 'Abuja'),
        ('uyo-abuja', 'Uyo / Abuja'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('remote-hybrid', 'Remote / Hybrid'),
    ]
    
    TYPE_CHOICES = [
        ('full-time', 'Full-Time'),
        ('part-time', 'Part-Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    job_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    description = models.TextField()
    requirements = models.TextField()
    is_featured = models.BooleanField(default=False)
    join_com_url = models.URLField(blank=True, null=True, help_text='Link to job posting on join.com')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class GeneralApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    position_applied = models.CharField(max_length=255, blank=True, help_text='Job title applied for (including unlisted roles)')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField()
    skills = models.TextField(help_text='Comma-separated list of skills')
    experience_years = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        position = self.position_applied or (self.job.title if self.job else 'General Application')
        return f"{self.first_name} {self.last_name} - {position}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"
