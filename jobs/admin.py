from django.contrib import admin
from .models import Job, Company, GeneralApplication


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)
    fields = ('name', 'description', 'order')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'job_type', 'join_com_url', 'created_at', 'is_featured')
    list_filter = ('location', 'job_type', 'is_featured', 'created_at')
    search_fields = ('title', 'description')
    fields = ('title', 'location', 'job_type', 'description', 'requirements', 'join_com_url', 'is_featured')
    ordering = ('-created_at',)


@admin.register(GeneralApplication)
class GeneralApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'position_applied', 'job', 'email', 'experience_years', 'created_at')
    list_filter = ('created_at', 'experience_years', 'job')
    search_fields = ('first_name', 'last_name', 'email', 'position_applied')
    readonly_fields = ('created_at',)
    fields = ('job', 'position_applied', 'first_name', 'last_name', 'email', 'phone', 'experience_years', 'skills', 'cover_letter', 'resume', 'created_at')
    ordering = ('-created_at',)
