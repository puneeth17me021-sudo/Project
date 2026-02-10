from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def seed_course_catalog(apps, schema_editor):
    CourseCategory = apps.get_model('custom_admin', 'CourseCategory')
    Course = apps.get_model('custom_admin', 'Course')

    catalog = {
        'Software Development': ['Python', 'HTML', 'CSS', 'JavaScript', 'React'],
        'Analysis': ['Data Analysis', 'Data Science'],
        'AI-ML': ['AI/ML', 'Machine Learning', 'Gen AI'],
        'Office': ['Office Automation', 'Advanced Excel'],
        'Accounting': [
            'Tally Essential Level 1',
            'Tally Essential Level 2',
            'Tally Essential Level 3',
            'Tally Comprehensive',
        ],
    }

    for category_name, courses in catalog.items():
        category, _ = CourseCategory.objects.get_or_create(name=category_name)
        for title in courses:
            Course.objects.get_or_create(
                category=category,
                title=title,
                defaults={
                    'description': f'{title} course under {category_name}.',
                    'level': 'beginner',
                    'duration_hours': 0,
                    'is_active': True,
                },
            )


def reverse_seed_course_catalog(apps, schema_editor):
    CourseCategory = apps.get_model('custom_admin', 'CourseCategory')
    CourseCategory.objects.filter(
        name__in=[
            'Software Development',
            'Analysis',
            'AI-ML',
            'Office',
            'Accounting',
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('custom_admin', '0002_sitebranding_websiteimage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Course categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                (
                    'level',
                    models.CharField(
                        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
                        default='beginner',
                        max_length=20,
                    ),
                ),
                ('duration_hours', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                (
                    'category',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='courses',
                        to='custom_admin.coursecategory',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='created_courses',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['category__name', 'title'],
                'unique_together': {('category', 'title')},
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                (
                    'visibility',
                    models.CharField(
                        choices=[('public', 'Public'), ('private', 'Private'), ('draft', 'Draft')],
                        default='public',
                        max_length=20,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'course',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='lessons',
                        to='custom_admin.course',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='created_lessons',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='CourseEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                (
                    'course',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='enrollments',
                        to='custom_admin.course',
                    ),
                ),
                (
                    'student',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='enrollments',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['-enrolled_at'],
                'unique_together': {('student', 'course')},
            },
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance_date', models.DateField()),
                ('source', models.CharField(choices=[('enroll', 'Enroll'), ('enter', 'Enter Course')], default='enter', max_length=20)),
                ('marked_at', models.DateTimeField(auto_now_add=True)),
                (
                    'course',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='attendance_records',
                        to='custom_admin.course',
                    ),
                ),
                (
                    'student',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='attendance_records',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['-attendance_date', '-marked_at'],
                'unique_together': {('student', 'course', 'attendance_date')},
            },
        ),
        migrations.RunPython(seed_course_catalog, reverse_seed_course_catalog),
    ]
