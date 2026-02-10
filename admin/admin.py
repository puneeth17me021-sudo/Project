from django.contrib import admin
from django.utils.html import format_html

from .models import (
    AttendanceRecord,
    Course,
    CourseCategory,
    CourseEnrollment,
    Lesson,
    SiteBranding,
    WebsiteImage,
)


@admin.register(SiteBranding)
class SiteBrandingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'logo_preview', 'updated_at')

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:38px;width:auto;border:1px solid #ddd;border-radius:4px;padding:2px;" />',
                obj.logo.url,
            )
        return '-'


@admin.register(WebsiteImage)
class WebsiteImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'page', 'is_active', 'image_preview', 'created_at')
    list_filter = ('page', 'is_active')
    search_fields = ('title',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:45px;width:auto;border:1px solid #ddd;border-radius:4px;padding:2px;" />',
                obj.image.url,
            )
        return '-'


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'duration_hours', 'is_active', 'created_at')
    list_filter = ('category', 'level', 'is_active')
    search_fields = ('title', 'description')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'visibility', 'lesson_file', 'created_at')
    list_filter = ('visibility', 'course__category')
    search_fields = ('title', 'description', 'course__title')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course__category',)
    search_fields = ('student__username', 'course__title')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'attendance_date', 'source', 'marked_at')
    list_filter = ('source', 'attendance_date', 'course__category')
    search_fields = ('student__username', 'course__title')
