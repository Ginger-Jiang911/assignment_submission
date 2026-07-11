from django.contrib import admin

from .models import Project, Submission


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "auto_rename", "storage_backend", "deadline", "created_at")
    list_filter = ("is_active", "auto_rename", "storage_backend")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("project", "student", "original_filename", "renamed_filename", "file_size", "appeal_submitted", "submitted_at")
    list_filter = ("project", "appeal_submitted", "submitted_at")
    search_fields = ("student__name", "student__student_id", "project__name")