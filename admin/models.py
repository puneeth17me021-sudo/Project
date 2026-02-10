from django.db import models
from django.conf import settings


class SiteBranding(models.Model):
    site_name = models.CharField(max_length=120, default='School Of IT Skills')
    logo = models.ImageField(upload_to='branding/logos/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Branding'
        verbose_name_plural = 'Site Branding'

    def __str__(self):
        return self.site_name


class WebsiteImage(models.Model):
    PAGE_CHOICES = [
        ('home', 'Home'),
        ('about', 'About'),
        ('course', 'Course'),
        ('testimonials', 'Testimonials'),
        ('contact', 'Contact'),
        ('global', 'Global'),
    ]

    title = models.CharField(max_length=120)
    image = models.ImageField(upload_to='website/images/')
    page = models.CharField(max_length=20, choices=PAGE_CHOICES, default='global')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CourseCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Course categories'

    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration_hours = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_courses',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category__name', 'title']
        unique_together = [('category', 'title')]

    def __str__(self):
        return f'{self.title} ({self.category.name})'


class Lesson(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('draft', 'Draft'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lesson_file = models.FileField(upload_to='lessons/files/', blank=True, null=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_lessons',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.course.title}'


class CourseEnrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('student', 'course')]
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.student.username} -> {self.course.title}'


class AttendanceRecord(models.Model):
    SOURCE_CHOICES = [
        ('enroll', 'Enroll'),
        ('enter', 'Enter Course'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_records')
    attendance_date = models.DateField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='enter')
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('student', 'course', 'attendance_date')]
        ordering = ['-attendance_date', '-marked_at']

    def __str__(self):
        return f'{self.student.username} {self.course.title} {self.attendance_date}'
